from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

VERSION = "0.1.0"


class T_Environment(StrEnum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"


class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    EXCEPTION = "exception"
    CRITICAL = "critical"


class LogConfiguration(BaseModel):
    level: LogLevel = Field(default=LogLevel.DEBUG)
    directory: Path = Field(default=Path("../../logs/"))
    retention: str = "10 Days"
    rotation: str = "10 MB"
    backtrace: bool = True
    enqueue: bool = True

    @field_validator("directory")
    @classmethod
    def ensure_directory(cls, source: Path) -> Path:
        source.expanduser().mkdir(exist_ok=True, parents=True)
        return source.expanduser().resolve()


class DatabaseConfiguration(BaseModel):
    username: str
    password: SecretStr
    host: str
    database: str
    port: int = 5432

    @property
    def connection_url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"


class Settings(BaseSettings):
    version: str = VERSION
    environment: T_Environment = T_Environment.DEVELOPMENT
    database: DatabaseConfiguration
    logging: LogConfiguration = Field(default_factory=LogConfiguration)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        env_nested_delimiter="__",
    )


settings = Settings()  # type: ignore[call-arg]
