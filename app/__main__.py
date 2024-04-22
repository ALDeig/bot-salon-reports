import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from commands import set_commands

from app.settings import settings
from app.src.dialogs.handlers import admin, user
from app.src.middleware.db import DbSessionMiddleware
from app.src.services.db.base import session_factory

logger = logging.getLogger(__name__)


def _include_routers(dp: Dispatcher):
    dp.include_routers(user.router, admin.router)


def _include_filters(admins: list[int], dp: Dispatcher):
    dp.message.filter(F.chat.type == "private")
    admin.router.message.filter(F.chat.id.in_(admins))


def _middleware_registry(dp: Dispatcher):
    dp.message.middleware(DbSessionMiddleware(session_factory))
    dp.callback_query.middleware(DbSessionMiddleware(session_factory))


async def main():
    bot = Bot(
        token=settings.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация фильтров
    _include_filters(settings.ADMINS, dp)

    # Регистрация middlewares
    _middleware_registry(dp)

    # Регистрация хендлеров
    _include_routers(dp)

    # Установка команд для бота
    await set_commands(bot, settings.ADMINS)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        logger.info("Bot starting...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.error("Bot stopping...")
