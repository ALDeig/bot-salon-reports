from datetime import datetime
import sqlalchemy as sa
from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.models import MAnswer, MQuestion, MReport, MSalon, MUser


class QuestionDao(BaseDao[MQuestion]):
    """Класс работы с базой данных для таблицы Question."""

    model = MQuestion


class AnswerDao(BaseDao[MAnswer]):
    """Класс работы с базой данных для таблицы Answer."""

    model = MAnswer


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
