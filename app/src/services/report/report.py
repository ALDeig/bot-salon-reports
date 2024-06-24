from collections.abc import Sequence
from datetime import datetime

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.services.db.dao.dao import QuestionDao, ReportDao, SalonDao
from app.src.services.db.models import MQuestion, MReport, MSalon
from app.src.services.exceptions import BadAnswerTypeError, ReportInitError
from app.src.services.report.enums import AnswerType
from app.src.services.sheets.sheet import get_data_from_sheet


async def open_shift_is_exists(db: AsyncSession, user_id: int) -> bool:
    report = await ReportDao(db).find_one_or_none(user_id=user_id, closed=None)
    return report is not None


async def get_salons(db: AsyncSession, **filter_by) -> Sequence[MSalon]:
    return await SalonDao(db).find_all(**filter_by)


async def close_shift(db: AsyncSession, salon_id: int) -> None:
    await SalonDao(db).update({"shift_is_close": True}, id=salon_id)


class Report:
    """Класс работы с отчетом."""

    def __init__(
        self,
        session: AsyncSession,
        report_id: int | None = None,
    ) -> None:
        self.report_id = report_id
        self._session = session

    async def init_report(self, salon_id: int, user_id: int) -> None:
        report = await ReportDao(self._session).add(
            MReport(salon_id=salon_id, user_id=user_id)
        )
        if report is None:
            raise ReportInitError
        await SalonDao(self._session).update({"shift_is_close": False}, id=salon_id)
        self.report_id = report.id
        await self._save_questions_from_sheet_for_report(report.id)

    async def _save_questions_from_sheet_for_report(self, report_id: int) -> None:
        sheet_data = await get_data_from_sheet()
        questions = []
        for row in sheet_data:
            question = MQuestion(
                report_id=report_id,
                text=row[0],
                description=row[2],
                type=AnswerType.Photo if row[4] else AnswerType.Text,
                is_require=bool(row[1]),
            )
            questions.append(question)
        await QuestionDao(self._session).add_all(questions)

    async def get_questions(self) -> Sequence[MQuestion]:
        if self.report_id is None:
            raise ReportInitError
        return await QuestionDao(self._session).find_all(report_id=self.report_id)

    async def save_answer(
        self, question: MQuestion, msg: Message
    ) -> Sequence[MQuestion]:
        if question.type == AnswerType.Text:
            if not msg.text:
                raise BadAnswerTypeError
            data = msg.text
        else:
            if not msg.photo:
                raise BadAnswerTypeError
            photo = msg.photo[-1]
            data = photo.file_id

        await QuestionDao(self._session).update({"answer": data}, id=question.id)
        return await self.get_questions()

    async def get_question(self, question_id: int) -> MQuestion:
        return await QuestionDao(self._session).find_one(id=question_id)

    async def close_report(self) -> bool:
        questions = await self.get_questions()
        for question in questions:
            if question.is_require and not question.answer:
                return False
        report_dao = ReportDao(self._session)
        await report_dao.update({"closed": datetime.now()}, id=self.report_id)  # noqa: DTZ005
        report = await report_dao.find_one(id=self.report_id)
        await SalonDao(self._session).update(
            {"shift_is_close": True}, id=report.salon_id
        )
        return True
