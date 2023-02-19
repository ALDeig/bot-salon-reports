from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command(commands="start"))
async def cmd_start(msg: Message):
    print(msg.chat.type)
    await msg.answer("Привет админ")


