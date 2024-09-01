import enum
from dataclasses import dataclass
import sqlalchemy as sqla
from sqlalchemy import Column
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from data.sqla_base import Base


class Status(enum.Enum):
    ACTIVE = 'active'
    BANNED = 'banned'


class Role(enum.Enum):
    ADMIN = 'admin'
    MASTER = 'master'


@dataclass
class BotUser(Base):
    __tablename__ = "users"

    telegram_user_id = mapped_column(sqla.BigInteger, primary_key=True, index=True, unique=True, nullable=False)
    status: Mapped[Status] = mapped_column(sqla.Enum(Status), index=True, nullable=False,
                                           server_default=Status.ACTIVE.name, default=Status.ACTIVE)
    role: str | None = Column(sqla.Enum(Role), index=True, nullable=True)

    def __init__(self, telegram_user_id: int, role: str = None, status=Status.ACTIVE):
        super().__init__()
        self.telegram_user_id = telegram_user_id
        self.role = role
        self.status = status

    def __repr__(self):
        return f"<User(telegram_user_id={self.telegram_user_id}, role={self.role})>"


@dataclass
class BannedUser(Base):
    __tablename__ = "banned_users"

    telegram_user_id = mapped_column(sqla.BigInteger, primary_key=True, index=True, unique=False, nullable=False)
    telegram_chat_id = mapped_column(sqla.BigInteger, primary_key=True, index=True, unique=False, nullable=False)
    date = mapped_column(sqla.DateTime(timezone=True), nullable=False)
    user_message = mapped_column(sqla.Text, nullable=True)
    reason = mapped_column(sqla.Text, nullable=True)
    omniban = mapped_column(sqla.Boolean, nullable=False)

    def __repr__(self):
        return f"<User(id={self.telegram_user_id}, chat={self.telegram_chat_id}, banned_on={self.date}, is_omniban={self.omniban}>"
