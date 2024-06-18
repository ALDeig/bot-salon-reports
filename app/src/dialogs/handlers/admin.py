from aiogram import Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.dialogs.keyboards.report import kb_salons
from app.src.services.report.data import get_salons
from app.src.services.report.report import send_report

router = Router()


@router.message(Command("get_report"), flags={"db": True})
async def cmd_get_report(msg: Message, db: AsyncSession, state: FSMContext):
    salons = await get_salons(db)
    kb = kb_salons(*salons)
    await state.update_data(salons=salons)
    await msg.answer("Выберите салон", reply_markup=kb)
    await state.set_state("get_report")


@router.message(StateFilter("get_report"), flags={"db": True})
async def btn_select_salon_for_check_report(
    msg: Message, db: AsyncSession, bot: Bot, state: FSMContext
):
    data = await state.get_data()
    await send_report(data["salons"][msg.text], bot, db)
