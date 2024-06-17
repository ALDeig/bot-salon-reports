from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.models import User


class UserDao(BaseDao[User]):
    """Класс работы с базой данных для таблицы User."""

    model = User
