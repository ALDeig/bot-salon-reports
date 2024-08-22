import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from aiogram.types import Message
from sqlalchemy.exc import NoResultFound

from app.src.services.db.dao.holder import HolderDao
from app.src.services.db.models import MQuestion, MReport, MSalon
from app.src.services.exceptions import BadAnswerTypeError, ReportInitError
from app.src.services.report.enums import AnswerType
from app.src.services.sheets.sheet import get_data_from_sheet

logger = logging.getLogger(__name__)


@dataclass
class OpenShift:
    """Класс работы с открытым отчетом."""

    salon: MSalon
    report: MReport


async def get_shift_is_exists(dao: HolderDao, user_id: int) -> OpenShift | None:
    report = await dao.report_dao.find_one_or_none(user_id=user_id, closed=None)
    if report is None:
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
            raise ReportInitError
        await self._dao.salon_dao.update({"shift_is_close": False}, id=salon_id)
        await self._save_questions_from_sheet_for_report(report.id)
        return report

    async def _save_questions_from_sheet_for_report(self, report_id: int) -> None:
        sheet_data = await get_data_from_sheet()
        questions = [
            MQuestion(
                report_id=report_id,
                text=row[0],
                description=row[2],
                type=AnswerType.Photo if row[4] else AnswerType.Text,
                is_require=bool(row[1]),
            )
            for row in sheet_data
        ]
        await self._dao.question_dao.add_all(questions)

    async def get_questions(self, report_id: int) -> Sequence[MQuestion]:
        return await self._dao.question_dao.find_all(report_id=report_id)

    async def save_answer(
        self, question: MQuestion, msg: Message
    ) -> None:
        if question.type == AnswerType.Text:
            if not msg.text:
                raise BadAnswerTypeError
            data = msg.text
        else:
            if not msg.photo:
                raise BadAnswerTypeError
            photo = msg.photo[-1]
            data = photo.file_id
        await self._dao.question_dao.update({"answer": data}, id=question.id)

    async def get_question(self, question_id: int) -> MQuestion:
        return await self._dao.question_dao.find_one(id=question_id)

    async def close_report(self, report_id: int) -> bool:
        questions = await self.get_questions(report_id)
        for question in questions:
            if question.is_require and not question.answer:
                return False
        await self._dao.report_dao.update({"closed": datetime.now()}, id=report_id)  # noqa: DTZ005
        try:
            report = await self._dao.report_dao.find_one(id=report_id)
        except NoResultFound:
            logger.error("Report not found: %s", report_id)  # noqa: TRY400
            return False
        await self._dao.salon_dao.update(
            {"shift_is_close": True}, id=report.salon_id
        )
        return True
