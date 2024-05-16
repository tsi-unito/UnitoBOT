from dataclasses import dataclass
from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column
from data.utils import SQLAlchemyBase


@dataclass
class BotChat(SQLAlchemyBase):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    added_on: Mapped[datetime] = mapped_column(server_default=sa.func.now(), nullable=False)
    telegram_chat_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, unique=True, nullable=False)

    def __init__(self, telegram_chat_id: int):
        super().__init__()
        # noinspection PyTypeChecker
        self.telegram_chat_id = telegram_chat_id

    def __repr__(self):
        return f"<Chat(id={self.id}, telegram_chat_id={self.telegram_chat_id}, added_on={self.added_on})>"
