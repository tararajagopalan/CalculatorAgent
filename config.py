"""Setup: logging, the Gemini key, and the model."""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

PROJECT_DIR = Path(__file__).resolve().parent  # this folder: holds .env and logs/

# 1. The log file: every log.info / log.error line goes to logs/calculator_agent.log.
LOG_FILE = PROJECT_DIR / "logs" / "calculator_agent.log"
log = logging.getLogger("calculator_agent")
if not log.handlers:  # don't add a second handler if a notebook re-imports this
    LOG_FILE.parent.mkdir(exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(module)s: %(message)s"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)

# 2. The key, from .env (git-ignored) or the environment. Stop at once if there isn't one.
load_dotenv(PROJECT_DIR / ".env")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    log.error("Missing key: GOOGLE_API_KEY")
    sys.exit("error: GOOGLE_API_KEY not set. Put it in .env (see .env.example).")

# 3. Which Gemini model, and how many steps an agent may take.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL") or "gemini-flash-latest"
MAX_AGENT_STEPS = 25  # stops a run that loops

# 4. The connection to Gemini, shared by both agents: 60-second timeout; one retry on timeouts,
#    rate limits and server errors.
llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0, google_api_key=GOOGLE_API_KEY,
                             timeout=60, max_retries=2)
