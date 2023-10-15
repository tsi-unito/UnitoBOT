from dataclasses import dataclass

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, registry

mapper_registry = registry()


# The annotation is needed to avoid having to declare a boilerplate class...
# https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html#declarative-mapping-using-a-decorator-no-declarative-base
@mapper_registry.mapped
@dataclass
class BotUser:
    __tablename__ = "users"

    # WARNING! We're missing the definition of the table. If you're developing this, please take a look at botchat.py

    telegram_user_id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(index=True, nullable=False)

    def __repr__(self):
        return f"<User(telegram_user_id={self.telegram_user_id}, role={self.role})>"
