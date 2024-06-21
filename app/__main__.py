import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.commands import set_commands
from app.settings import settings
from app.src.dialogs.handlers import admin, report, user
from app.src.middleware.db import DbSessionMiddleware
from app.src.services.db.base import session_factory
from app.src.services.scheduler import create_scheduler_tasks

logger = logging.getLogger(__name__)


def _include_routers(dp: Dispatcher) -> None:
    """Подключает роуты."""
    dp.include_routers(user.router, admin.router, report.router)


def _include_filters(admins: list[int], dp: Dispatcher) -> None:
    """Подключает фильтры."""
    dp.message.filter(F.chat.type == "private")
    admin.router.message.filter(F.chat.id.in_(admins))


def _middleware_registry(dp: Dispatcher) -> None:
    """Подключает middleware."""
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

    # init scheduler
    scheduler = create_scheduler_tasks()

    try:
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=True)
        await bot.session.close()


if __name__ == "__main__":
    try:
        logger.info("Bot starting...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot stopping...")
