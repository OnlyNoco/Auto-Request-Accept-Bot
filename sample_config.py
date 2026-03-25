import os
import logging
from logging.handlers import RotatingFileHandler

# Copy this file to `config.py` (DO NOT commit `config.py`) or set env vars.

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
WORKER = int(os.environ.get("WORKER", "4"))
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
PORT = os.environ.get("PORT", "8080")

DB_URL = os.environ.get("DB_URL", "")
DB_NAME = os.environ.get("DB_NAME", "")

START_MSG = os.environ.get(
    "START_MSG",
    "<blockquote>Hello {mention}</blockquote>\n\n"
    "<b>Add me as admin in your private chats, "
    "and I can approve join requests automatically.</b>",
)

CMD_MSG = os.environ.get(
    "CMD_MSG",
    "<blockquote>/start - check bot\n/help - help\n/report - report issue</blockquote>",
)

START_PIC = os.environ.get("START_PIC", "").split(" ") if os.environ.get("START_PIC") else []
FLOOD_WAIT = int(os.environ.get("FLOOD_WAIT", "10"))
BROADCAST_DELETE_TIME = int(os.environ.get("BROADCAST_DELETE_TIMED", "18"))

# LOGGER SETUP
LOG_FILE_NAME = "onlynoco.txt"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10,
        ),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

