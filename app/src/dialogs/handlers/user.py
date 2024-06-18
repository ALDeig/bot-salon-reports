from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer("Для отправки отчета введите команду /report")
