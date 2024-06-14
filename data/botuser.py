import enum
from dataclasses import dataclass
import sqlalchemy as sqla
from sqlalchemy import Column
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

Base = declarative_base()


class Status(enum.Enum):
    ACTIVE = 'active'
    BANNED = 'banned'


class Role(enum.Enum):
    ADMIN = 'admin'
    MASTER = 'master'


@dataclass
class BotUser(Base):
    __tablename__ = "users"

    telegram_user_id: int = Column(sqla.BigInteger, primary_key=True, index=True, unique=True, nullable=False)
    status: Status = Column(sqla.Enum(Status),
                            index=True, nullable=False, server_default=Status.ACTIVE.name, default=Status.ACTIVE)
    role: str | None = Column(sqla.Enum(Role), index=True, nullable=True)

    def __init__(self, telegram_user_id: int, role: str = None, status=Status.ACTIVE):
        super().__init__()
        # noinspection PyTypeChecker
        self.telegram_user_id = telegram_user_id
        # noinspection PyTypeChecker
        self.role = role
        self.status = status

    def __repr__(self):
        return f"<User(telegram_user_id={self.telegram_user_id}, role={self.role})>"
