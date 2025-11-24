"""Configuration file with settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import computed_field, PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


SERVICE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Contains env variables and other app's settings.
    env searching order:
    - os environ,
    - .env file,
    - default values setted here
    """

    model_config = SettingsConfigDict(
        env_file=f"{SERVICE_DIR}/.env", env_file_encoding="utf-8", extra="ignore"
    )

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            path=self.POSTGRES_DB,
        )

    WEATHER_PROVIDER_API_KEY: str = Field(
        description="API Key to get access to the weather provider",
    )

    MINIO_ADDRESS: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "weather"

    DEBUG: bool = False


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
