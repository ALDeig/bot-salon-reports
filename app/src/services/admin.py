from collections.abc import Sequence

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.services.db.dao.dao import UserDao, ReportDao
from app.src.services.db.models import MQuestion, MReport, MUser
from app.src.services.report.enums import AnswerType


class CheckReport:
    """Проверка отчетов."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_reports(self, salon_id: int) -> Sequence[MReport]:
        return await ReportDao(self._session).find_all(salon_id=salon_id)

    async def send_report(self, msg: Message, report_id: int) -> None:
        report = await ReportDao(self._session).find_one(id=report_id)
        user = await UserDao(self._session).find_one(id=report.user_id)
        if not report.closed:
            await msg.answer(self._text_not_done_report(report.questions, user))
            return
        await msg.answer(
            f"Отчет от администратора: @{user.username}/{user.full_name}\n"
            f"Смена открыта: {report.created}\nСмена закрыта: {report.closed}"
        )
        for question in report.questions:
            answer = question.answer
            if not answer:
                await msg.answer(
                    f"<b>{question.text}</b>\n\n<em>Задание пропущено.</em>"
                )
                continue
            if question.type == AnswerType.Photo:
                await msg.answer_photo(question.answer.data, caption=question.text)
            else:
                await msg.answer(
                    f"<b>{question.text}</b>\n\n<em>{question.answer.data}</em>"
                )

    @staticmethod
    def _text_not_done_report(questions: Sequence[MQuestion], user: MUser) -> str:
        done_questions = (
            f"<b>Отчет от администратора: @{user.username} / {user.full_name}\n"
            f"Выполненные задания:</b>\n\n"
        )
        not_done_questions = "<b>Невыполненные задания:</b>\n\n"
        for question in questions:
            if question.answer:
                done_questions += f"{question.text}\n\n"
            else:
                not_done_questions += f"{question.text}\n\n"
        return done_questions + not_done_questions
