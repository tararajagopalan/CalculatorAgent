"""Calculator agent: give it arithmetic in plain English, get the answer in plain English.

Run it with

    python main.py
    What would you like to calculate? (type quit or exit to stop) add 2 to 5 then divide the result by 3.5

It keeps asking until you type quit or exit (or press Ctrl-C / Ctrl-D).

It reads instructions from the keyboard, so you can also feed it text instead of typing, eg. from a script:

    python main.py <<< 'add 2 to 5 then divide the result by 3.5'

When the text runs out it stops, as if you'd typed quit.

Gemini works out the steps; the add, subtract, multiply and divide tools do the arithmetic. Each
instruction runs through both versions of the agent (agent.run and agent.run2) and prints both answers.
Each step is logged to logs/calculator_agent.log.
"""
import sys

from agent import run, run2

PROMPT = "What would you like to calculate? (type quit or exit to stop) "
STOP_WORDS = {"quit", "exit"}


def calculate(instruction):
    """Run the instruction through both versions and print what each returns."""
    # 1. The version built by create_agent.
    answer, error = run(instruction)
    print("[create_agent]", answer or f"error: {error}")

    # 2. The hand-written version.
    answer, error = run2(instruction)
    print("[hand-written loop]", answer or f"error: {error}")


def main(args):
    """args is the list of words typed after `python main.py`. There are no options, so it should be
    empty: instructions are typed when the program asks for them."""

    # 1. Nothing should follow main.py.
    if len(args) > 0:
        print(f"error: didn't understand {' '.join(args)!r}. Run main.py on its own and type your\n"
              "instruction when asked.", file=sys.stderr)
        return 1

    # 2. Keep asking until the user stops.
    while True:
        # 2a. Ask. Ctrl-D or Ctrl-C stops, and so does running out of input.
        try:
            instruction = input(PROMPT).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        # 2b. quit or exit (in any capitals) stops.
        if instruction.lower() in STOP_WORDS:
            return 0

        # 2c. Calculate. A blank line just asks again.
        if instruction:
            calculate(instruction)
            print()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
