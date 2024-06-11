import asyncio
import logging
from alembic import command
from alembic.config import Config
from core.db import database
from core.config import BOT_TOKEN, API_HASH, API_ID
from handlers import start, user_tasks
from pyrogram import Client
from pyrogram_patch import patch
from pyrogram_patch.fsm.storages import MemoryStorage


async def start_bot(app: Client):
    await app.start()


async def start_db(app: Client):
    await database.connect()
    await app.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    alembic_cfg = Config("./alembic.ini")
    command.upgrade(alembic_cfg, "head")
    loop = asyncio.get_event_loop()
    app = Client(bot_token=BOT_TOKEN, name="test", api_hash=API_HASH, api_id=API_ID)

    patch_manager = patch(app)
    patch_manager.set_storage(MemoryStorage())
    patch_manager.include_router(start.router)
    patch_manager.include_router(user_tasks.router)
    loop.create_task(start_db(app))
    loop.run_forever()

