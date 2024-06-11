from repository.db import DatabaseRepository
from repository.tools import get_values
from schema.user_tasks import user_tasks
import sqlalchemy


class UserTasksRepository(DatabaseRepository):
    """Class Repository for manage User Tasks table using SQLAlchemy ORM."""

    @staticmethod
    async def create(values: dict) -> int:
        query = user_tasks.insert().values(values)
        return await DatabaseRepository.execute(query)

    @staticmethod
    async def get_all(user_id: int, skip: int = 0, limit: int = 14) -> list[dict]:
        query = (user_tasks.select()
                 .where(user_tasks.c.user_id == user_id)
                 .limit(limit)
                 .offset(skip*limit))
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_by_chat_id(chat_id: str) -> dict:
        query = sqlalchemy.select(user_tasks).where(user_tasks.c.chat_id == chat_id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_by_id(id: int) -> dict:
        query = user_tasks.select().where(user_tasks.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def update(id: int, values: dict) -> any:
        query = user_tasks.update().values(values).where(user_tasks.c.id == id)
        return await DatabaseRepository.execute(query)

    @staticmethod
    async def delete(id: int) -> any:
        query = user_tasks.delete().where(user_tasks.c.id == id)
        return await DatabaseRepository.execute(query)
