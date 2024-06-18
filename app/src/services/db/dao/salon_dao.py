from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.models import Salon


class SalonDao(BaseDao[Salon]):
    """Класс работы с базой данных для таблицы Salon."""

    model = Salon
