import logging

from pydantic import BaseSettings, PostgresDsn, RedisDsn, validator


class Config(BaseSettings):
    bot_token: str
    bot_fsm_storage: str
    admins: list[int]
    postgres_dsn: PostgresDsn | None
    sqlite_dsn: str | None
    redis_dsn: RedisDsn | None

    @validator("bot_fsm_storage")
    def validate_fsm_storage(cls, v):
        if v not in ("memory", "redis"):
            raise ValueError("Incorrect 'bot_fsm_storage' value. Value mast be 'memory' or 'redis'")
        return v

    @validator("redis_dsn")
    def validate_redis_dsn(cls, v, values):
        if values["bot_fsm_storage"] == "redis" and not v:
            raise ValueError("Redis DSN string is missing!")
        return v

    @validator("sqlite_dsn")
    def validate_sqlite_dsn(cls, v, values):
        if values["postgres_dsn"]:
            return
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Config()


def logging_setup(skip_loggers_list: list[str] | None = None):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s %(name)s - %(module)s:%(funcName)s:%(lineno)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    if skip_loggers_list is not None:
        for logger_name in skip_loggers_list:
            logging.getLogger(logger_name).propagate = False


