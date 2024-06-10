import sqlalchemy
import enum
from core.db import metadata


class TaskStatuses(enum.Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'


user_tasks = sqlalchemy.Table(
    "user_tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("description", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("status", sqlalchemy.Enum(TaskStatuses), nullable=False, default=TaskStatuses.PENDING),
    sqlalchemy.Column("complete_till", sqlalchemy.DateTime, nullable=True),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, nullable=False, default=sqlalchemy.func.now()),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, default=sqlalchemy.func.now()),
)
