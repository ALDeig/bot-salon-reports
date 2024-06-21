import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
)

logger = logging.getLogger(__name__)

ADMIN_COMMANDS = [
    BotCommand(command="start", description="Перезапустить бот"),
    BotCommand(command="get_report", description="Получить отчёт"),
]
USER_COMMANDS = [
    BotCommand(command="start", description="Перезапустить бот"),
    BotCommand(command="report", description="Отправить отчёт"),
]


async def set_commands(bot: Bot, admins: list[int]):
    await bot.set_my_commands(
        commands=USER_COMMANDS,
        scope=BotCommandScopeAllPrivateChats(),
    )
    for admin in admins:
        try:
            await bot.set_my_commands(
                ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=admin)
            )
        except TelegramBadRequest:
            logging.warning("Can't set commands to admin with ID %s", admin)
