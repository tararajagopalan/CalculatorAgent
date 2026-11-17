# Calculator agent

Give it arithmetic in plain English ("add 2 to 5 then divide the result by 3.5") and it answers in
plain English. Gemini works out the steps; the add, subtract, multiply and divide tools do the arithmetic.

New to agents? Open [guide.html](guide.html) in a browser: it walks through the whole program, top down,
including how LangChain's agents and the ReAct loop work.

## Set up (once)

### 1. Get a Gemini API key

1. Go to [Google AI Studio's API keys page](https://aistudio.google.com/apikey) and sign in with
   your Google account.
2. Click **Create API key**. If it asks for a Google Cloud project, pick one or let it create one.
3. Copy the key. Keep it private: anyone with it can use your Gemini quota.

The key works on Gemini's free tier, which has usage limits; see Google's Gemini API pricing page
for the current limits and paid rates.

### 2. Install and add the key

On a Mac (or Linux), in Terminal:

```sh
cd calculatoragent
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

On Windows 11, in PowerShell:

```powershell
cd path\to\calculatoragent
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

If you do not have a `.env` file with proper keys, then follow these steps:

```sh
cp .env.example .env                 # Mac or Linux
Copy-Item .env.example .env          # Windows (PowerShell)
```

Then open `.env` and paste the key after `GOOGLE_API_KEY=`:

```
GOOGLE_API_KEY=your-key-here
```

`.env` can also set `GEMINI_MODEL` (default: `gemini-flash-latest`). It is git-ignored, so the key
is never committed. A key can also come from the environment instead: `export GOOGLE_API_KEY=...`.

## Run

```sh
.venv/bin/python main.py             # Mac or Linux
.venv\Scripts\python main.py         # Windows
```

It keeps asking "What would you like to calculate?" until you type `quit` or `exit`.

It reads your instructions from the keyboard, so a script can feed it text instead of typing. When the
text runs out, it stops as if you'd typed `quit`. Use single quotes, so the shell leaves the text alone:

```sh
.venv/bin/python main.py <<< 'multiply 3 by 4'

.venv/bin/python main.py <<'END'
add 2 to 5 then divide the result by 3.5
multiply 3 by 4
END
```

Each step is logged to `logs/calculator_agent.log`.
