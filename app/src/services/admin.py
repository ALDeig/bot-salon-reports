import logging
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.exc import NoResultFound

from app.src.services.db.dao.holder import HolderDao
from app.src.services.db.models import MQuestion, MReport, MUser
from app.src.services.report.enums import AnswerType

logger = logging.getLogger(__name__)


@dataclass
class CheckReportResponse:
    """Ответ проверки отчета."""

    state: str
    report: MReport | None = None
    user: MUser | None = None


class CheckReport:
    """Проверка отчетов."""

    def __init__(self, dao: HolderDao) -> None:
        self._dao = dao

    async def get_reports(self, salon_id: int) -> Sequence[MReport]:
        return await self._dao.report_dao.find_all(salon_id=salon_id)

    async def check_report(self, report_id: int) -> CheckReportResponse:
        try:
            report = await self._dao.report_dao.find_one(id=report_id)
        except NoResultFound:
            logger.warning("Report not found: %s", report_id)
            return CheckReportResponse(state="report_not_found")
        user = await self._dao.user_dao.find_one(id=report.user_id)
        if not report.closed:
            return CheckReportResponse(state="not_done", report=report, user=user)
        return CheckReportResponse(state="done", report=report, user=user)


def text_not_done_report(questions: Sequence[MQuestion], user: MUser) -> str:
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


def messages_done_report(report: MReport, user: MUser) -> list[str | tuple[str, str]]:
    messages = []
    messages.append(
        f"Отчет от администратора: @{user.username}/{user.full_name}\n"
        f"Смена открыта: {report.created}\nСмена закрыта: {report.closed}"
    )
    for question in report.questions:
        if not question.answer:
            messages.append(f"<b>{question.text}</b>\n\n<em>Задание пропущено.</em>")
            continue
        if question.type == AnswerType.Photo:
            messages.append((question.answer, question.text))
        else:
            messages.append(f"<b>{question.text}</b>\n\n<em>{question.answer}</em>")
    return messages
