from dataclasses import dataclass
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

from bot import Base


@dataclass
class Question(Base):
    __tablename__ = "nlp_questions"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    message_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    message: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(server_default=sa.func.now(), nullable=False)
    feedbacks: Mapped[list["Feedback"]] = relationship(back_populates="question")

    def __init__(self, message_id: int, user_id: int, message: str):
        super().__init__()
        # noinspection PyTypeChecker
        self.message_id = message_id
        # noinspection PyTypeChecker
        self.user_id = user_id
        # noinspection PyTypeChecker
        self.message = message

    def __repr__(self):
        return f"<Question(id={self.id}, message_id={self.message_id}, user_id={self.user_id}, message={self.message}, date={self.date})>"


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many
    question_id: Mapped[int] = mapped_column(sa.ForeignKey(f"{Question.__tablename__}.id"), index=True)
    question: Mapped["Question"] = relationship(back_populates="feedbacks")
    user_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, index=True)
    value: Mapped[str] = mapped_column(index=True)
    raw_data: Mapped[str] = mapped_column()

    def __init__(self, question_id: int, user_id: int, value: str, raw_data: str | None = None):
        super().__init__()
        # noinspection PyTypeChecker
        self.question_id = question_id
        # noinspection PyTypeChecker
        self.user_id = user_id
        # noinspection PyTypeChecker
        self.value = value
        # noinspection PyTypeChecker
        self.raw_data = raw_data

    def __repr__(self):
        return (f"<Feedback(id={self.id}, question_id={self.question_id}, user_id={self.user_id}, value={self.value}, "
                f"raw_data={self.raw_data})>")
