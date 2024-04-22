from aiogram import Router, html
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession


router = Router()


@router.message(Command("start"), flags={"db": True})
async def cmd_start(msg: Message, db: AsyncSession):
    await save_user(db, msg.chat.id, msg.chat.full_name, msg.chat.username)
    await msg.answer(f"Hello {html.quote(msg.chat.full_name)}!")

