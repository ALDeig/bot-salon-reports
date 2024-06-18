from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from app.src.services.exceptions import BadAnswerTypeError
from app.src.services.report.data import get_questions
from app.src.services.report.report import finish_report, parse_answer, send_question

router = Router()


@router.message(Command("report"))
async def cmd_new_report(msg: Message, state: FSMContext) -> None:
    await msg.answer("Собираю вопросы... Подождите не много!")
    questions = await get_questions()
    if question := questions.get(1):
        await send_question(question, msg)
        await state.update_data(
            number=1, type=question.type, answers=[], questions=questions
        )
        await state.set_state("report")
        return
    await msg.answer("Нет вопросов")
    await state.clear()


@router.message(
    StateFilter("report"), F.content_type.in_((ContentType.TEXT, ContentType.PHOTO))
)
async def get_answer(msg: Message, bot: Bot, state: FSMContext) -> None:
    data = await state.get_data()
    try:
        answer = parse_answer(data["number"], data["type"], msg)
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
    await finish_report(msg.chat.username, data["questions"], data["answers"], bot)
    await msg.answer("Отчет отправлен")
    await state.clear()


@router.callback_query(StateFilter("report"), F.message.as_("msg"))
async def btn_skip(call: CallbackQuery, msg: Message, bot: Bot, state: FSMContext):
    await call.answer()
    await msg.edit_reply_markup()
    data = await state.get_data()
    if question := data["questions"].get(data["number"] + 1):
        await send_question(question, msg)
        await state.update_data(number=data["number"] + 1, type=question.type)
        return
    await finish_report(data["questions"], data["answers"], bot)
    await msg.answer("Отчет отправлен")
    await state.clear()
