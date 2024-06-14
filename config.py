from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    telegram_api_key: str = Field(..., env="TELEGRAM_API_KEY")
    database_url: PostgresDsn = Field(..., env="DATABASE_URL")
