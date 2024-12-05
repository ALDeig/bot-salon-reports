import logging

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from app.src.dialogs.keyboards.report import kb_questions, kb_salons
from app.src.services.db.dao.holder import HolderDao
from app.src.services.exceptions import (
    BadAnswerTypeError,
    ReportInitError,
    ReportIsClosedError,
    ReportNotFoundError,
)
from app.src.services.report.report import Report, get_salons, get_shift_is_exists

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("report"), flags={"dao": True})
async def cmd_new_report(msg: Message, dao: HolderDao, state: FSMContext):
    shift = await get_shift_is_exists(dao, msg.chat.id)
    if shift:
        kb = kb_questions(shift.report.questions)
        await msg.answer(
            f"У вас есть открытая смена в салоне: {shift.salon.name}", reply_markup=kb
        )
        return
    salons = await get_salons(dao, shift_is_close=True)
    if not salons:
        await msg.answer("Во всех салонах смены открыты.")
        return
    kb = kb_salons(salons)
    await state.update_data(salons=salons)
    await msg.answer("Выбери салон", reply_markup=kb)
    await state.set_state("select_salon")


@router.callback_query(
    StateFilter("select_salon"),
    F.message.as_("msg"),
    F.data.as_("data"),
    flags={"dao": True},
)
async def btn_select_salon(
    call: CallbackQuery, msg: Message, data: str, dao: HolderDao, state: FSMContext
) -> None:
    await msg.delete()
    await call.answer("Собираю вопросы... Подождите не много!")
    report_manager = Report(dao)
    try:
        report = await report_manager.init_report(int(data), msg.chat.id)
    except ReportInitError as er:
        await msg.answer(er.message)
    else:
        questions = await report_manager.get_questions(report.id)
        kb = kb_questions(questions)
        await msg.answer("Выбери вопрос", reply_markup=kb)
    finally:
        await state.clear()


@router.callback_query(
    F.data.startswith("ask"),
    F.data.as_("data"),
    F.message.as_("msg"),
    flags={"dao": True},
)
async def btn_question(
    call: CallbackQuery, msg: Message, data: str, dao: HolderDao, state: FSMContext
):
    await msg.delete()
    await call.answer(cache_time=30)
    _, question_id, report_id = data.split(":")
    try:
        question = await Report(dao).get_question(int(question_id))
    except ReportIsClosedError:
        await msg.answer(
            "Эта смена закрыта. "
            "Нажмите /report чтобы открыть новую смену или продолжить открытую"
        )
    else:
        await state.update_data(question=question, report_id=int(report_id))
        await msg.answer(f"{question.text}\n\n{question.description}")
        await state.set_state("report")


@router.message(
    StateFilter("report"),
    F.content_type.in_((ContentType.TEXT, ContentType.PHOTO)),
    flags={"dao": True},
)
async def get_answer(msg: Message, dao: HolderDao, state: FSMContext) -> None:
    data = await state.get_data()
    report = Report(dao=dao)  # report_id=data["report_id"])
    try:
        await report.save_answer(data["question"], msg)
    except BadAnswerTypeError:
        await msg.answer("Неверный формат ответа")
        return
    questions = await report.get_questions(data["report_id"])
    kb = kb_questions(questions)
    await msg.answer("Ответ сохранен", reply_markup=kb)
    await state.clear()


@router.callback_query(
    F.data.startswith("finish"),
    F.message.as_("msg"),
    F.data.as_("data"),
    flags={"dao": True},
)
async def btn_close_shift(call: CallbackQuery, msg: Message, data: str, dao: HolderDao):
    await call.answer()
    report = Report(dao)  # report_id=int(data.split(":")[-1]))
    try:
        report_status = await report.close_report(int(data.split(":")[-1]))
    except ReportNotFoundError:
        logger.warning(
            "Report not found by user: %s, %s",
            call.from_user.id,
            call.from_user.username,
        )
        await msg.answer("Ошибка закрытия смены. Попробуйте закрыть повторно.")
    else:
        if report_status:
            await msg.delete()
            text = (
                f"Смена в салоне {report_status.salon} закрыта!\n"
                f"Все обязательные задания выполнены.\n"
                f"Вопросов: {report_status.questions}\n"
                f"Ответов: {report_status.answers}"
            )
        else:
            text = "Не все обязательные задания выполнены."
        await msg.answer(text)
