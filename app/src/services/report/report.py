from aiogram import Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import settings
from app.src.dialogs.keyboards.report import kb_skip
from app.src.services.db.dao.report_dao import ReportDao
from app.src.services.exceptions import BadAnswerTypeError
from app.src.services.report.data import Answer, Question
from app.src.services.report.enums import AnswerType


async def send_question(question: Question, msg: Message):
    kb = kb_skip if not question.require else None
    await msg.answer(f"{question.text}\n\n{question.description}", reply_markup=kb)


def parse_answer(
    number: int, report_type: AnswerType, msg: Message, question: str
) -> Answer:
    if report_type == AnswerType.Text:
        if not msg.text:
            raise BadAnswerTypeError
        data = msg.text
    else:
        if not msg.photo:
            raise BadAnswerTypeError
        photo = msg.photo[-1]
        data = photo.file_id
    return Answer(number=number, data=data, type=report_type, question=question)


async def finish_report(salon_id: int, answers: list[Answer], db: AsyncSession):
    answers_json = [answer.model_dump() for answer in answers]
    await ReportDao(db).insert_or_update(
        "id", {"answers"}, id=salon_id, answers=answers_json
    )


async def send_report(salon_id: int, bot: Bot, db: AsyncSession):
    report = await ReportDao(db).find_one_or_none(id=salon_id)
    if report is None:
        await send_message(bot, "Нет отчета")
        return
    answers = [Answer.model_validate(answer) for answer in report.answers]
    text = ""
    for answer in answers:
        if answer.type == AnswerType.Text:
            text += f"<b>{answer.question}</b>\n{answer.data}\n\n"
        else:
            if text:
                await send_message(bot, text)
                text = ""
            await send_message(bot, answer.question, answer.data)
    await send_message(bot, f"{text}\n\n<b>Конец отчета</b>".strip())
    await ReportDao(db).delete(id=salon_id)


async def send_message(bot: Bot, text: str, photo: str | None = None) -> None:
    for admin in settings.ADMINS:
        if photo:
            await bot.send_photo(admin, photo, caption=text)
        else:
            await bot.send_message(admin, text)
