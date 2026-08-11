from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


class SettingsConfig(BaseSettings):
    """
    Настройки приложения.
    """

    FINAM_RSS_URL: str = (
        "https://www.finam.ru/analysis/conews/rsspoint/"
    )

    REQUEST_TIMEOUT: int = 30

    USER_AGENT: str = "RSSNews/1.0"

    LOG_LEVEL: str = "INFO"

    LOGS_DIR: Path = BASE_DIR / "logs"

    DATA_DIR: Path = BASE_DIR / "data"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = SettingsConfig()


settings.LOGS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

settings.DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)