from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.dialogs.keyboards.report import kb_salons
from app.src.services.exceptions import BadAnswerTypeError
from app.src.services.report.data import get_questions, get_salons
from app.src.services.report.report import finish_report, parse_answer, send_question

router = Router()


@router.message(Command("report"), flags={"db": True})
async def cmd_new_report(msg: Message, db: AsyncSession, state: FSMContext):
    salons = await get_salons(db)
    kb = kb_salons(*salons)
    await state.update_data(salons=salons)
    await msg.answer("Выбери салон", reply_markup=kb)
    await state.set_state("select_salon")


@router.message(StateFilter("select_salon"))
async def btn_select_salon(msg: Message, state: FSMContext) -> None:
    await msg.answer(
        "Собираю вопросы... Подождите не много!", reply_markup=ReplyKeyboardRemove()
    )
    questions = await get_questions()
    if question := questions.get(1):
        data = await state.get_data()
        salon = data["salons"][msg.text]
        await send_question(question, msg)
        await state.update_data(
            salon_id=salon,
            number=1,
            type=question.type,
            answers=[],
            questions=questions,
        )
        await state.set_state("report")
        return
    await msg.answer("Нет вопросов")
    await state.clear()


@router.message(
    StateFilter("report"),
    F.content_type.in_((ContentType.TEXT, ContentType.PHOTO)),
    flags={"db": True},
)
async def get_answer(msg: Message, db: AsyncSession, state: FSMContext) -> None:
    data = await state.get_data()
    question = data["questions"][data["number"]]
    try:
        answer = parse_answer(data["number"], data["type"], msg, question.text)
    except BadAnswerTypeError:
        await msg.answer("Неверный формат ответа")
        return
    data["answers"].append(answer)
    if question := data["questions"].get(data["number"] + 1):
        await send_question(question, msg)
        await state.update_data(
            number=data["number"] + 1, type=question.type, answers=data["answers"]
        )
        return
    await finish_report(data["salon_id"], data["answers"], db)
    await msg.answer("Отчет сохранен")
    await state.clear()


@router.callback_query(StateFilter("report"), F.message.as_("msg"), flags={"db": True})
async def btn_skip(
    call: CallbackQuery, msg: Message, db: AsyncSession, state: FSMContext
):
    await call.answer()
    await msg.edit_reply_markup()
    data = await state.get_data()
    if question := data["questions"].get(data["number"] + 1):
        await send_question(question, msg)
        await state.update_data(number=data["number"] + 1, type=question.type)
        return
    await finish_report(data["salon_id"], data["answers"], db)
    await msg.answer("Отчет сохранен")
    await state.clear()
