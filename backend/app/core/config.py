
# BaseSettings reads configuration from environment variables and .env.
# database_url tells SQLAlchemy where PostgreSQL is running.
# settings gives the rest of our backend one consistent way to access configuration.
# Keeping credentials in .env means we don't hardcode passwords in Python files.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    resend_api_key: str
    email_from: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
