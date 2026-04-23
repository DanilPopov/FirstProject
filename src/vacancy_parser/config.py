from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./vacancy_parser.db",
        alias="DATABASE_URL",
    )

    hh_user_agent: str = Field(
        default="VacancyParserBot/0.1 (contact@example.com)",
        alias="HH_USER_AGENT",
    )
    hh_fetch_interval_seconds: int = Field(default=300, alias="HH_FETCH_INTERVAL_SECONDS")

    trial_duration_hours: int = Field(default=24, alias="TRIAL_DURATION_HOURS")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


settings = Settings()
