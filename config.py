from os import getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = getenv("API_TOKEN", "")
DB_PATH = Path(getenv("DB_PATH", Path(__file__).parent / "menubot.db"))
