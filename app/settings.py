import logging.config

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    TELEGRAM_TOKEN: str
    ADMINS: list[int]
    LOG_LEVEL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    SQLITE_DSN: str | None = None

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()  # type: ignore


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {
            "format": "[%(asctime)s] [%(levelname)-7s] [%(name)s] > %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "stream_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default_formatter",
        },
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default_formatter",
            "filename": "logs/app.log",
            "maxBytes": 1024 * 1024,
            "backupCount": 3
        },

    },
    "loggers": {
        "root": {
            "handlers": ["stream_handler", "file_handler"],
            "level": settings.LOG_LEVEL,
            "propagate": True,
        },
        "httpx": {
            "handlers": ["stream_handler"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}


logging.config.dictConfig(LOGGING_CONFIG)
