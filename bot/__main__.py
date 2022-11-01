import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.fsm.storage.redis import RedisStorage

from configreader import config
from commands import set_commands
from bot.src.dialogs.handlers import admin, user
from bot.src.middleware.db import DbSessionMiddleware
from bot.src.services.db.db_connect import create_session



def include_routers(dp: Dispatcher):
    dp.include_router(admin.router)
    dp.include_router(user.router)


def include_filters(admins: list[int], dp: Dispatcher):
    dp.message.filter(F.chat.type == "private")
    admin.router.message.filter(F.chat.id.in_(admins))


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    bot = Bot(token=config.bot_token, parse_mode="HTML")
    if config.bot_fsm_storage == "redis":
        raise ValueError("redis is not install")
        # storage = RedisStorage(config.redis_dsn)
    else:
        storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    session = create_session(config.sqlite_dsn)

    # Регистрация фильтров
    include_filters(config.admins, dp)

    # Регистрация middlewares
    dp.message.middleware(DbSessionMiddleware(session))

    # Регистрация хендлеров
    include_routers(dp)

    # Установка команд для бота
    await set_commands(bot, config)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()



if __name__ == "__main__":
    try:
        # logger.info("Bot starting...")
        asyncio.run(main())
    except KeyboardInterrupt:
        # logger.error("Bot stopping...")
