from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Table, Column, Integer, BigInteger, String, DateTime, func
from sqlalchemy.orm import registry

mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class Question:
    _tablename = "nlp_questions"
    __table__ = Table(
        _tablename,
        mapper_registry.metadata,
        Column("id", Integer(), primary_key=True, nullable=False),
        Column("message_id", BigInteger(), index=True, unique=True, nullable=False),
        Column("user_id", BigInteger(), index=True, unique=True, nullable=False),
        Column("message", String(), nullable=False),
        Column("date", DateTime(), server_default=func.now(), nullable=False)
    )

    id: int
    message_id: int
    user_id: int
    message: str
    date: datetime

    def __init__(self, message_id: int, user_id: int, message: str):
        self.message_id = message_id
        self.user_id = user_id
        self.message = message

    def __repr__(self):
        return f"<Question(id={self.id}, message_id={self.message_id}, user_id={self.user_id}, message={self.message}, date={self.date})>"
