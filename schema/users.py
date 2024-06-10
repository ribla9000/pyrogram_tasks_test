import sqlalchemy
from core.db import metadata


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("username", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("first_name", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("last_name", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("nickname", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("login_name", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("chat_id", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, default=sqlalchemy.func.now())
)
