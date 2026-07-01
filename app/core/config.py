from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field, SecretStr
from enum import StrEnum

VERSION = "0.1.0"


class T_Environment(StrEnum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"


class DatabaseConfiguration(BaseModel):
    username: str
    password: SecretStr
    host: str
    database: str
    port: int = 5432


class Settings(BaseSettings):
    version: str = VERSION
    environment: T_Environment = T_Environment.DEVELOPMENT
    database: DatabaseConfiguration

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        env_nested_delimiter="__",
    )


settings = Settings()  # pyright: ignore
