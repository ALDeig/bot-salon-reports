from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.src.services.db.dao.holder import HolderDao
from app.src.services.user import save_user

router = Router()


@router.message(Command("start"), flags={"dao": True})
async def cmd_start(msg: Message, state: FSMContext, dao: HolderDao):
    await state.clear()
    await save_user(dao, msg.chat.id, msg.chat.full_name, msg.chat.username)
    await msg.answer("Для отправки отчета введите команду /report")
