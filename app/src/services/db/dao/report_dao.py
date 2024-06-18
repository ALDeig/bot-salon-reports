from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.models import Report


class ReportDao(BaseDao[Report]):
    """Класс работы с базой данных для таблицы Report."""

    model = Report
