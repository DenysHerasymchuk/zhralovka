from os import getenv
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = getenv("API_TOKEN", "")
LOG_LEVEL = getenv("LOG_LEVEL", "INFO").upper()
DB_PATH = Path(getenv("DB_PATH", Path(__file__).parent / "menubot.db"))
TIMEZONE = ZoneInfo("Europe/Brussels")
DEEPL_API_KEY = getenv("DEEPL_API_KEY", "")
