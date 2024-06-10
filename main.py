import asyncio
import logging
import threading
from alembic import command
from alembic.config import Config
from core.db import database
from core.config import BOT_TOKEN, API_HASH, API_ID
from handlers import start, user_tasks
from pyrogram import Client
from pyrogram_patch import patch


def start_db():
    asyncio.run(database.connect())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    alembic_cfg = Config("./alembic.ini")
    command.upgrade(alembic_cfg, "head")
    app = Client(bot_token=BOT_TOKEN, name="test-task", api_hash=API_HASH, api_id=API_ID)

    patch_manager = patch(app)
    patch_manager.include_router(start.router)
    patch_manager.include_router(user_tasks.router)

    thread_db = threading.Thread(target=start_db)
    thread_db.start()
    thread_bot = threading.Thread(app.run())
    thread_bot.start()
