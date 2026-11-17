"""Two versions of the same calculator agent. Give either an instruction like "add 2 to 5 then divide
the result by 3.5" and get the answer back in plain English.

  run()   uses LangChain's create_agent, which builds the agent loop for us.
  run2()  is the same loop written out by hand.

Both return (answer, None) on success, or (None, error) if the run failed, and never raise.
"""
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.errors import GraphRecursionError
from pydantic import ValidationError

from config import MAX_AGENT_STEPS, llm, log
from tools import add, divide, multiply, subtract

SYSTEM_PROMPT = """You are a calculator. Work through the user's instruction one step at a time, in the order given.
Do every calculation with a tool (add, subtract, multiply, divide), one operation per call, and never
calculate anything yourself. Use each result in the next step, exactly as the tool returned it.
When you're done, answer in one or two plain English sentences: what you did, step by step, and the
final result. If a tool returns an error, stop and explain the error instead."""

TOOLS = [add, subtract, multiply, divide]


def gemini_failed(exc):
    return f"Gemini failed: {type(exc).__name__}: {str(exc)[:300]}"


# ---- Version 1: create_agent builds the loop

agent = create_agent(llm, tools=TOOLS, system_prompt=SYSTEM_PROMPT)


def run(instruction):
    """The agent built by create_agent."""
    log.info("run: %s", instruction)
    # 1. Run the whole agent loop. It comes back when Gemini replies without asking for a tool.
    try:
        state = agent.invoke({"messages": [("user", instruction)]}, config={"recursion_limit": MAX_AGENT_STEPS})
    except GraphRecursionError:
        # 2. It went round too many times: stop.
        log.error("run: took more than %d steps; stopped", MAX_AGENT_STEPS)
        return None, "The agent took too many steps and was stopped. Try a shorter instruction."
    except Exception as exc:
        # 3. Gemini failed: down, timed out twice, key rejected, ...
        log.exception("run: Gemini failed")
        return None, gemini_failed(exc)

    # 4. The last message is Gemini's final reply, after all its tool calls.
    answer = state["messages"][-1].text.strip()
    if not answer:
        log.error("run: Gemini gave an empty answer")
        return None, "Gemini didn't give an answer."

    # 5. Done.
    log.info("run: answer: %s", answer)
    return answer, None


# ---- Version 2: the same loop, written by hand

tools_by_name = {t.name: t for t in TOOLS}
model_with_tools = llm.bind_tools(TOOLS)  # tells Gemini which tools exist and what arguments they take


def run_tool(call):
    """Run one tool Gemini asked for, and return its result as text (an error message if it can't)."""
    # 1. Find the tool Gemini asked for.
    tool = tools_by_name.get(call["name"])
    if tool is None:
        log.error("run2: Gemini asked for a tool that doesn't exist: %s", call["name"])
        return f"Error: there is no tool called {call['name']}."

    # 2. Run it with the arguments Gemini sent.
    try:
        return tool.invoke(call["args"])
    except ValidationError as exc:
        # 3. Bad arguments, eg. a word instead of a number: say what's wrong, so Gemini can fix it.
        problems = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors())
        log.error("run2: %s%s: bad arguments: %s", call["name"], call["args"], problems)
        return f"Error: {call['name']} got bad arguments ({problems}). Fix them and try again."
    except Exception as exc:
        # 4. Anything else went wrong inside the tool.
        log.error("run2: %s%s failed: %s", call["name"], call["args"], exc)
        return f"Error: {call['name']} failed ({type(exc).__name__}: {exc})."


def run2(instruction):
    """The hand-written agent loop: ask Gemini, run the tools it asks for, repeat until it answers."""
    log.info("run2: %s", instruction)
    # 0. Start the conversation. Gemini sees all of it every time round, so it knows each result.
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(instruction)]

    for step in range(MAX_AGENT_STEPS):
        # 1. Ask Gemini what to do next.
        try:
            reply = model_with_tools.invoke(messages)
        except Exception as exc:  # Gemini down, timed out twice, key rejected, ...
            log.exception("run2: Gemini failed")
            return None, gemini_failed(exc)
        messages.append(reply)

        # 2. No tools asked for: this reply is the final answer.
        if not reply.tool_calls:
            answer = reply.text.strip()
            if not answer:
                log.error("run2: Gemini gave an empty answer")
                return None, "Gemini didn't give an answer."
            log.info("run2: answer after %d steps: %s", step + 1, answer)
            return answer, None

        # 3. Run each tool Gemini asked for, and add its result to the conversation.
        for call in reply.tool_calls:
            result = run_tool(call)
            messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
        # 4. Back to the top: Gemini sees the tool results and decides the next step.

    # 5. It went round too many times: stop.
    log.error("run2: took more than %d steps; stopped", MAX_AGENT_STEPS)
    return None, "The agent took too many steps and was stopped. Try a shorter instruction."
