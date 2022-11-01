from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command(commands="start"))
async def cmd_start(msg: Message):
    await msg.answer(f"Hello {html.quote(msg.from_user.full_name)}!")

