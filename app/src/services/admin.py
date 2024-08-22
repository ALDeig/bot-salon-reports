from collections.abc import Sequence

from aiogram.types import Message

from app.src.services.db.dao.holder import HolderDao
from app.src.services.db.models import MQuestion, MReport, MUser
from app.src.services.report.enums import AnswerType


class CheckReport:
    """Проверка отчетов."""

    def __init__(self, dao: HolderDao) -> None:
        self._dao = dao

    async def get_reports(self, salon_id: int) -> Sequence[MReport]:
        return await self._dao.report_dao.find_all(salon_id=salon_id)

    async def send_report(self, msg: Message, report_id: int) -> None:
        report = await self._dao.report_dao.find_one(id=report_id)
        user = await self._dao.user_dao.find_one(id=report.user_id)
        if not report.closed:
            await msg.answer(self._text_not_done_report(report.questions, user))
            return
        await msg.answer(
            f"Отчет от администратора: @{user.username}/{user.full_name}\n"
            f"Смена открыта: {report.created}\nСмена закрыта: {report.closed}"
        )
        for question in report.questions:
            if not question.answer:
                await msg.answer(
                    f"<b>{question.text}</b>\n\n<em>Задание пропущено.</em>"
                )
                continue
            if question.type == AnswerType.Photo:
                await msg.answer_photo(question.answer, caption=question.text)
            else:
                await msg.answer(
                    f"<b>{question.text}</b>\n\n<em>{question.answer}</em>"
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
