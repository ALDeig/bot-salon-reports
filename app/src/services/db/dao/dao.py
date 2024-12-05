from collections.abc import Sequence
from datetime import datetime

import sqlalchemy as sa

from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.models import MQuestion, MReport, MSalon, MUser


class QuestionDao(BaseDao[MQuestion]):
    """Класс работы с базой данных для таблицы Question."""

    model = MQuestion

    async def find_all_order_by_answer(self, **filter_by) -> Sequence[MQuestion]:
        query = sa.select(self.model).filter_by(**filter_by).order_by(self.model.answer)
        response = await self._session.scalars(query)
        return response.all()


class ReportDao(BaseDao[MReport]):
    """Класс работы с базой данных для таблицы Report."""

    model = MReport

    async def delete_old_reports(self, check_date: datetime) -> None:
        query = sa.delete(self.model).where(self.model.created < check_date)
        await self._session.execute(query)
        await self._session.commit()


class SalonDao(BaseDao[MSalon]):
    """Класс работы с базой данных для таблицы Salon."""

    model = MSalon


class UserDao(BaseDao[MUser]):
    """Класс работы с базой данных для таблицы User."""

    model = MUser
