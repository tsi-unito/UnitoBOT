from dataclasses import dataclass
import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped, declarative_base

from bot import Base


@dataclass
class Setting(Base):
    __tablename__ = "persistent_settings"

    setting_name: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    value: Mapped[str] = mapped_column(nullable=False, server_default='')

    def __init__(self, name: str, value: str):
        super().__init__()
        # noinspection PyTypeChecker
        self.setting_name = name
        # noinspection PyTypeChecker
        self.value = value

    def __repr__(self):
        return f"<Setting(name={self.setting_name}, value={self.value})>"

    def __str__(self):
        return f"{self.setting_name}: {self.value}"
