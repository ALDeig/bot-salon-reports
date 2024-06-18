from aiogram import Bot
from aiogram.types import Message

from app.settings import settings
from app.src.dialogs.keyboards.report import kb_skip
from app.src.services.exceptions import BadAnswerTypeError
from app.src.services.report.data import Answer, Question
from app.src.services.report.enums import AnswerType


async def send_question(question: Question, msg: Message):
    kb = kb_skip if not question.require else None
    await msg.answer(f"{question.text}\n\n{question.description}", reply_markup=kb)


def parse_answer(number: int, report_type: AnswerType, msg: Message) -> Answer:
    if report_type == AnswerType.Text:
        if not msg.text:
            raise BadAnswerTypeError
        data = msg.text
    else:
        if not msg.photo:
            raise BadAnswerTypeError
        photo = msg.photo[-1]
        data = photo.file_id
    return Answer(number=number, data=data, type=report_type)


async def finish_report(
    username: str, questions: dict[int, Question], answers: list[Answer], bot: Bot
):
    text = ""
    await send_message(bot, f"Отчет от администратора с ником: {username}")
    for answer in answers:
        question_text = questions[answer.number].text
        if answer.type == AnswerType.Text:
            text += f"<b>{question_text}</b>\n{answer.data}\n\n"
        else:
            if text:
                await send_message(bot, text)
                text = ""
            await send_message(bot, question_text, answer.data)
    await send_message(bot, f"{text}\n\n<b>Конец отчета</b>".strip())


async def send_message(bot: Bot, text: str, photo: str | None = None) -> None:
    for admin in settings.ADMINS:
        if photo:
            await bot.send_photo(admin, photo, caption=text)
        else:
            await bot.send_message(admin, text)

