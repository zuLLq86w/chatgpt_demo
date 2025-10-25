import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self
from sqlalchemy.engine import URL
from loguru import logger


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    SENTRY_DSN: HttpUrl | None = None
    MYSQL_SERVER: str
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = ""


    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> URL:
        return URL.create(
            "mysql+aiomysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_SERVER,
            port=self.MYSQL_PORT,
            database=self.MYSQL_DB,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI_SYNC(self) -> URL:
        return URL.create(
            "mysql+pymysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_SERVER,
            port=self.MYSQL_PORT,
            database=self.MYSQL_DB,
        )

    AES_KEY: str

    REDIS_HOST: str = "localhost:6379"
    REDIS_USER: str = 'default'
    REDIS_PASSWORD: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URI(self) -> str:
        # "redis://[[username]:[password]]@localhost:6379/0"
        if self.REDIS_PASSWORD and self.REDIS_USER:
            return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}"
        else:
            return f"redis://{self.REDIS_HOST}"

    # 日志
    LOG_LEVEL: str = "INFO"
    STDERR_LOG: bool = True
    DEBUG_LOG: bool = True
    ERROR_LOG: bool = True

    PROFILE: bool = False
    DEEPSEEK_API_KEY: str


settings = Settings()
logger.info(settings)