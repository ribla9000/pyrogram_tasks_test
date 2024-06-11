import typing
from core.db import database
from databases import Database
from databases.interfaces import Record
from sqlalchemy.sql.elements import ClauseElement

class DatabaseRepository:
    """Class Repository for using ORM methods. If necessary, override methods from the ORM"""

    @staticmethod
    def fetch_all(query: typing.Union[ClauseElement, str], values: typing.Optional[dict] = None) -> typing.Coroutine:
        return Database.fetch_all(self=database, query=query, values=values)

    @staticmethod
    def fetch_one(query: typing.Union[ClauseElement, str], values: typing.Optional[dict] = None) -> typing.Coroutine:
        return Database.fetch_one(self=database, query=query, values=values)

    @staticmethod
    def execute(query: typing.Union[ClauseElement, str],values: typing.Optional[dict] = None) -> typing.Coroutine:
        return Database.execute(self=database, query=query, values=values)
