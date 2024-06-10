import os
from dotenv import load_dotenv
load_dotenv(".env")


BOT_TOKEN = os.getenv("ENV_BOT_TOKEN")
API_HASH = os.getenv("ENV_API_HASH")
API_ID = os.getenv("ENV_API_ID")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
ENV = os.getenv("ENV")

BACK_BUTTON_TEXT = "🔙 Назад"
SKIP_BUTTON_TEXT = "Skip >>"
ARROW_LEFT = "⬅️"
ARROW_RIGHT = "➡️"
NONE_FUNCTION = "#None#null#0"
