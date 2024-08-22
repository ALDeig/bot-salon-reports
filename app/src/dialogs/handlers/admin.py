from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.src.dialogs.keyboards.admin import kb_select_report
from app.src.dialogs.keyboards.report import kb_salons
from app.src.services.admin import CheckReport
from app.src.services.db.dao.holder import HolderDao
from app.src.services.report.report import close_shift, get_salons

router = Router()


@router.message(Command("get_report"), flags={"dao": True})
async def cmd_get_report(msg: Message, dao: HolderDao, state: FSMContext):
    salons = await get_salons(dao)
    await msg.answer("Выберите салон", reply_markup=kb_salons(salons))
    await state.set_state("select_salon_admin")


@router.callback_query(
    StateFilter("select_salon_admin"),
    F.message.as_("msg"),
    F.data.as_("data"),
    flags={"dao": True},
)
async def btn_select_salon_for_check_report(
    call: CallbackQuery,
    msg: Message,
    data: str,
    dao: HolderDao,
    state: FSMContext,
):
    await call.answer()
    checker = CheckReport(dao)
    reports = await checker.get_reports(int(data))
    await msg.answer("Выбери отчет", reply_markup=kb_select_report(reports))
    await state.set_state("select_report")


@router.callback_query(
    StateFilter("select_report"),
    F.message.as_("msg"),
    F.data.as_("data"),
    flags={"dao": True},
)
async def btn_select_report(
    call: CallbackQuery, msg: Message, data: str, dao: HolderDao, state: FSMContext
):
    await call.answer()
    checker = CheckReport(dao)
    await checker.send_report(msg, int(data))
    await msg.answer("Готово")
    await state.clear()


@router.message(Command("close_shift"), flags={"dao": True})
async def cmd_close_shift(msg: Message, dao: HolderDao, state: FSMContext):
    salons = await get_salons(dao, shift_is_close=False)
    if not salons:
        await msg.answer("Все смены закрыты")
        return
    await msg.answer("Выберите салон", reply_markup=kb_salons(salons))
    await state.set_state("close_shift")


@router.callback_query(
    StateFilter("close_shift"),
    F.message.as_("msg"),
    F.data.as_("data"),
    flags={"dao": True},
)
async def btn_select_shift_for_close(
    call: CallbackQuery, msg: Message, data: str, dao: HolderDao, state: FSMContext
):
    await call.answer()
    await close_shift(dao, int(data))
    await msg.answer("Смена закрыта.")
    await state.clear()
