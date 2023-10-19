from dataclasses import dataclass

from sqlalchemy.orm import Mapped, mapped_column
from data.utils import SQLAlchemyBase


@dataclass
class BotUser(SQLAlchemyBase):
    __tablename__ = "users"

    telegram_user_id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(index=True, nullable=False)

    def __init__(self, telegram_user_id: int, role: str):
        super().__init__()
        # noinspection PyTypeChecker
        self.telegram_user_id = telegram_user_id
        # noinspection PyTypeChecker
        self.role = role

    def __repr__(self):
        return f"<User(telegram_user_id={self.telegram_user_id}, role={self.role})>"
