from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.dialogs.keyboards.report import kb_questions, kb_salons
from app.src.services.exceptions import BadAnswerTypeError
from app.src.services.report.report import Report, get_salons, open_shift_is_exists

router = Router()


@router.message(Command("report"), flags={"db": True})
async def cmd_new_report(msg: Message, db: AsyncSession, state: FSMContext):
    shift_is_exist = await open_shift_is_exists(db, msg.chat.id)
    if shift_is_exist:
        await msg.answer("У вас есть открытая смена.")
        return
    salons = await get_salons(db, shift_is_close=True)
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
    flags={"db": True},
)
async def btn_select_salon(
    call: CallbackQuery, msg: Message, data: str, db: AsyncSession, state: FSMContext
) -> None:
    await call.answer("Собираю вопросы... Подождите не много!")
    report = Report(db)
    await report.init_report(int(data), msg.chat.id)
    questions = await report.get_questions()
    kb = kb_questions(questions)
    await msg.answer("Выбери вопрос", reply_markup=kb)
    await state.clear()


@router.callback_query(
    F.data.startswith("ask"),
    F.data.as_("data"),
    F.message.as_("msg"),
    flags={"db": True},
)
async def btn_question(
    call: CallbackQuery, msg: Message, data: str, db: AsyncSession, state: FSMContext
):
    await call.answer()
    _, question_id, report_id = data.split(":")
    question = await Report(db).get_question(int(question_id))
    await state.update_data(question=question, report_id=int(report_id))
    await msg.answer(f"{question.text}\n\n{question.description}")
    await state.set_state("report")


@router.message(
    StateFilter("report"),
    F.content_type.in_((ContentType.TEXT, ContentType.PHOTO)),
    flags={"db": True},
)
async def get_answer(msg: Message, db: AsyncSession, state: FSMContext) -> None:
    data = await state.get_data()
    report = Report(session=db, report_id=data["report_id"])
    try:
        questions = await report.save_answer(data["question"], msg)
    except BadAnswerTypeError:
        await msg.answer("Неверный формат ответа")
        return
    kb = kb_questions(questions)
    await msg.answer("Ответ сохранен", reply_markup=kb)
    await state.clear()


@router.callback_query(
    F.data.startswith("finish"),
    F.message.as_("msg"),
    F.data.as_("data"),
    flags={"db": True},
)
async def btn_close_shift(
    call: CallbackQuery, msg: Message, data: str, db: AsyncSession
):
    await call.answer()
    report = Report(db, report_id=int(data.split(":")[-1]))
    is_done = await report.close_report()
    text = "Готово!" if is_done else "Не все обязательные задания выполнены."
    await msg.answer(text)
