import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
)

logger = logging.getLogger(__name__)

ADMIN_COMMANS = [
    BotCommand(command="start", description="Перезапустить бот"),
]


async def set_commands(bot: Bot, admins: list[int]):
    await bot.set_my_commands(
        commands=[BotCommand(command="start", description="Перезапустить бот")],
        scope=BotCommandScopeAllPrivateChats(),
    )
    for admin in admins:
        try:
            await bot.set_my_commands(
                ADMIN_COMMANS, scope=BotCommandScopeChat(chat_id=admin)
            )
        except TelegramBadRequest as er:
            logging.error(f"Can't set commands to admin with ID {admin}: {er.message}")
