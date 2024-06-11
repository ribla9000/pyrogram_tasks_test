from repository.db import DatabaseRepository
from repository.tools import get_values
from schema.users import users
import sqlalchemy


class UsersRepository(DatabaseRepository):
    """Class Repository for manage Users table using SQLAlchemy ORM."""

    @staticmethod
    async def create(values: dict) -> int:
        query = users.insert().values(values)
        return await DatabaseRepository.execute(query)

    @staticmethod
    async def get_all(skip: int, limit: int = 14) -> list[dict]:
        query = (users.select()
                 .limit(limit)
                 .offset(skip*limit))
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_by_chat_id(chat_id: str) -> dict:
        query = sqlalchemy.select(users).where(users.c.chat_id == chat_id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_by_id(id: int) -> dict:
        query = users.select().where(users.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def update(id: int, values: dict) -> int:
        query = users.update().values(values).where(users.c.id == id)
        return await DatabaseRepository.execute(query)

    @staticmethod
    async def get_by_login(login: str) -> dict:
        query = users.select().where(users.c.login_name == login)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)
