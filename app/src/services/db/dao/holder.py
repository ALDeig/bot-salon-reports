import logging
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.dao.dao import QuestionDao, ReportDao, SalonDao, UserDao
from app.src.services.db.dao.exceptions import DaoNotFoundError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseDao)


class HolderDao:
    """Содержит или инициализирует все экземпляры DAO."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_dao: UserDao | None = None
        self._salon_dao: SalonDao | None = None
        self._report_dao: ReportDao | None = None
        self._question_dao: QuestionDao | None = None

    @property
    def user_dao(self) -> UserDao:
        return self._get_dao("user_dao", UserDao)

    @property
    def salon_dao(self) -> SalonDao:
        return self._get_dao("salon_dao", SalonDao)

    @property
    def report_dao(self) -> ReportDao:
        return self._get_dao("report_dao", ReportDao)

    @property
    def question_dao(self) -> QuestionDao:
        return self._get_dao("question_dao", QuestionDao)

    def _get_dao(self, dao_name: str, dao: type[T]) -> T:
        try:
            val = getattr(self, f"_{dao_name}")
        except AttributeError as er:
            logger.exception("Not field %s for DAO object", dao_name)
            raise DaoNotFoundError from er
        if not val:
            val = dao(self._session)
            setattr(self, f"_{dao_name}", val)
        return val
