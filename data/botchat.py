from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, Table, Column, Integer, DateTime, BigInteger, Sequence
from sqlalchemy.orm import Mapped, mapped_column, registry, DeclarativeBase

mapper_registry = registry()


# The annotation is needed to avoid having to declare a boilerplate class...
# https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html#declarative-mapping-using-a-decorator-no-declarative-base
@mapper_registry.mapped
@dataclass
class BotChat:
    _tablename = "chats"
    _id_seq = Sequence(_tablename+"_id_seq")
    __table__ = Table(
        _tablename,
        mapper_registry.metadata,
        Column("id", Integer(), primary_key=True, server_default=_id_seq.next_value(), nullable=False), #primary_key=True, index=True, unique=True, nullable=False, autoincrement=True),
        Column("added_on", DateTime(), server_default=func.now(), nullable=False),
        Column("telegram_chat_id", BigInteger(), index=True, unique=True, nullable=False)
    )

    id: int
    added_on: datetime
    telegram_chat_id: int

    def __init__(self, telegram_chat_id: int):
        self.telegram_chat_id = telegram_chat_id

    def __repr__(self):
        return f"<Chat(id={self.id}, telegram_chat_id={self.telegram_chat_id}, added_on={self.added_on})>"
