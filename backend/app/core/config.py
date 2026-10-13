
# BaseSettings reads configuration from environment variables and .env.
# database_url tells SQLAlchemy where PostgreSQL is running.
# settings gives the rest of our backend one consistent way to access configuration.
# Keeping credentials in .env means we don't hardcode passwords in Python files.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
