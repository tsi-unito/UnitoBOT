from dataclasses import dataclass
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


class SQLAlchemyBase(DeclarativeBase):
    pass


@dataclass
class Question(SQLAlchemyBase):
    __tablename__ = "nlp_questions"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    message_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    message: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(server_default=sa.func.now(), nullable=False)

    def __init__(self, message_id: int, user_id: int, message: str):
        # noinspection PyTypeChecker
        self.message_id = message_id
        # noinspection PyTypeChecker
        self.user_id = user_id
        # noinspection PyTypeChecker
        self.message = message
        super().__init__()

    def __repr__(self):
        return f"<Question(id={self.id}, message_id={self.message_id}, user_id={self.user_id}, message={self.message}, date={self.date})>"

# class Feedback(DeclarativeBase):
#     __tablename__ = "feedbacks"
#
#     id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
#     question_id: Mapped
