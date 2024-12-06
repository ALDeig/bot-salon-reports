import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from aiogram.types import Message
from sqlalchemy.exc import NoResultFound

from app.src.services.db.dao.holder import HolderDao
from app.src.services.db.models import MQuestion, MReport, MSalon
from app.src.services.exceptions import (
    BadAnswerTypeError,
    QuestionTypeUnknownError,
    ReportInitError,
    ReportIsClosedError,
    ReportNotFoundError,
)
from app.src.services.report.enums import AnswerType
from app.src.services.sheets.sheet import get_data_from_sheet

logger = logging.getLogger(__name__)


@dataclass
class OpenShift:
    """Класс работы с открытым отчетом."""

    salon: MSalon
    report: MReport


@dataclass(slots=True, frozen=True)
class ReportStatus:
    """Статус отчета."""

    salon: str
    questions: int
    answers: int


async def get_shift_is_exists(dao: HolderDao, user_id: int) -> OpenShift | None:
    report = await dao.report_dao.find_one_or_none(user_id=user_id, closed=None)
    if report is None:
        return
    if not report.questions:
        await dao.report_dao.update({"closed": datetime.now()}, id=report.id)  # noqa: DTZ005
        await dao.salon_dao.update({"shift_is_close": True}, id=report.salon_id)
        logger.warning("В сохраненном отчете нет вопросов. Report_id: %s", report.id)
        return
    salon = await dao.salon_dao.find_one(id=report.salon_id)
    return OpenShift(salon=salon, report=report)


async def get_salons(dao: HolderDao, **filter_by) -> Sequence[MSalon]:
    return await dao.salon_dao.find_all(**filter_by)


async def close_shift(dao: HolderDao, salon_id: int) -> None:
    report = await dao.report_dao.find_one_or_none(salon_id=salon_id, closed=None)
    if report:
        await dao.report_dao.update({"closed": datetime.now()}, id=report.id)  # noqa: DTZ005
    await dao.salon_dao.update({"shift_is_close": True}, id=salon_id)


class Report:
    """Класс работы с отчетом."""

    def __init__(self, dao: HolderDao) -> None:
        self._dao = dao

    async def init_report(self, salon_id: int, user_id: int) -> MReport:
        report = await self._dao.report_dao.add(
            MReport(salon_id=salon_id, user_id=user_id)
        )
        if report is None:
            raise ReportInitError(
                message="Не удалось инициализировать отчет. Попробуйте еще раз."
            )
        try:
            await self._save_questions_from_sheet_for_report(report.id)
        except ReportInitError:
            await self._dao.report_dao.delete(id=report.id)
            raise
        await self._dao.salon_dao.update({"shift_is_close": False}, id=salon_id)
        return report

    async def _save_questions_from_sheet_for_report(self, report_id: int) -> None:
        sheet_data = await get_data_from_sheet()
        try:
            questions = [
                MQuestion(
                    report_id=report_id,
                    text=row[0],
                    description=row[2],
                    type=_get_type_answer(row),
                    is_require=bool(row[1]),
                )
                for row in sheet_data
                if row
            ]
        except (IndexError, QuestionTypeUnknownError) as er:
            raise ReportInitError(
                message="Не удалось собрать вопросы из таблицы. Попробуйте еще раз."
            ) from er
        await self._dao.question_dao.add_all(questions)

    async def get_questions(self, report_id: int) -> Sequence[MQuestion]:
        return await self._dao.question_dao.find_all_order_by_answer(
            report_id=report_id
        )

    async def save_answer(self, question: MQuestion, msg: Message) -> None:
        match question.type:
            case AnswerType.Text:
                if not msg.text:
                    raise BadAnswerTypeError
                data = msg.text
            case AnswerType.Photo:
                if not msg.photo:
                    raise BadAnswerTypeError
                photo = msg.photo[-1]
                data = photo.file_id
            case AnswerType.Video:
                if not msg.video_note:
                    raise BadAnswerTypeError
                data = msg.video_note.file_id

        await self._dao.question_dao.update({"answer": data}, id=question.id)

    async def get_question(self, question_id: int) -> MQuestion:
        question = await self._dao.question_dao.find_one(id=question_id)
        report = await self._dao.report_dao.find_one_or_none(id=question.report_id)
        if not report or report.closed:
            raise ReportIsClosedError
        return question

    async def close_report(self, report_id: int) -> ReportStatus | None:
        try:
            report = await self._dao.report_dao.find_one(id=report_id)
        except NoResultFound as er:
            logger.warning("Report not found: %s", report_id)
            raise ReportNotFoundError from er
        for question in report.questions:
            if question.is_require and not question.answer:
                return
        await self._dao.report_dao.update({"closed": datetime.now()}, id=report_id)  # noqa: DTZ005
        await self._dao.salon_dao.update({"shift_is_close": True}, id=report.salon_id)
        return await self._get_report_status(report)

    async def _get_report_status(self, report: MReport) -> ReportStatus:
        salon = await self._dao.salon_dao.find_one(id=report.salon_id)
        answers = 0
        for question in report.questions:
            if question.answer:
                answers += 1
        return ReportStatus(
            salon=salon.name, questions=len(report.questions), answers=answers
        )


def _get_type_answer(row: list[str]) -> AnswerType:
    """Возвращает тип ответа."""
    match row:
        case _ if row[3]:
            return AnswerType.Video
        case _ if row[4]:
            return AnswerType.Photo
        case _ if row[5]:
            return AnswerType.Text
        case _:
            logger.warning("Unknown question type: %s", row)
            raise QuestionTypeUnknownError
