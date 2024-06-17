import logging
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.services.db.base import Base

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=Base)


class BaseDao(Generic[T]):
    """Базовый класс для DAO (Data Access Object) с общими методами для взаимодействия
    с базой данных.

    Атрибуты:
        model (type[T]): Модель базы данных, с которой работает DAO.
        _session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.
    """

    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует экземпляр BaseDao.

        Args:
        ----
            session (AsyncSession): Асинхронная сессия для взаимодействия с базой
            данных.

        """
        self._session = session
        super().__init__()

    async def find_all(self, **filter_by) -> Sequence[T]:
        """Возвращает все записи, соответствующие заданным фильтрам.

        Args:
        ----
            filter_by: Произвольное количество именованных аргументов для фильтрации.

        Returns:
        -------
            Sequence[T]: Последовательность найденных записей.

        """
        query = sa.select(self.model).filter_by(**filter_by)
        response = await self._session.scalars(query)
        return response.all()

    async def find_one_or_none(self, **filter_by) -> T | None:
        """Возвращает одну запись, соответствующую заданным фильтрам, или None, если
        запись не найдена.

        Args:
        ----
            filter_by: Произвольное количество именованных аргументов для фильтрации.

        Returns:
        -------
            T | None: Найденная запись или None.

        """
        query = sa.select(self.model).filter_by(**filter_by)
        return await self._session.scalar(query)

    async def find_one(self, **filter_by) -> T:
        """Возвращает одну запись, соответствующую заданным фильтрам. Если запись не
        найдена, выбрасывает исключение.

        Args:
        ----
            filter_by: Произвольное количество именованных аргументов для фильтрации.

        Returns:
        -------
            T: Найденная запись.

        Raises:
        ------
            NoResultFound: Если запись не найдена.

        """
        query = sa.select(self.model).filter_by(**filter_by)
        response = await self._session.execute(query)
        return response.scalar_one()

    async def add(self, model_instance: T) -> T | None:
        """Добавляет новую запись в базу данных.

        Args:
        ----
            model_instance (T): Экземпляр модели для добавления.

        Returns:
        -------
            T | None: Добавленная запись или None в случае ошибки.

        """
        self._session.add(model_instance)
        try:
            await self._session.commit()
        except IntegrityError:
            logger.exception("IntegrityError. Data: %s", model_instance)
            await self._session.rollback()
            return None
        return model_instance

    async def insert_or_update(
        self, index_element: str, update_fields: set[str], **data
    ) -> None:
        """Выполняет вставку или обновление записи в базе данных.

        Args:
        ----
            index_element (str): Поле для индексации (уникальный ключ).
            update_fields (set[str]): Набор полей для обновления при конфликте.
            data: Произвольное количество данных для вставки или обновления.

        """
        query = (
            insert(self.model)
            .values(**data)
            .on_conflict_do_update(
                index_elements=[index_element],
                set_={key: data[key] for key in update_fields if key in data},
            )
        )
        await self._session.execute(query)
        await self._session.commit()

    async def insert_or_nothing(self, index_element: str, **data) -> None:
        """Выполняет вставку новой записи или ничего не делает при конфликте.

        Args:
        ----
            index_element (str): Поле для индексации (уникальный ключ).
            data: Произвольное количество данных для вставки.

        """
        query = (
            insert(self.model)
            .values(**data)
            .on_conflict_do_nothing(index_elements=[index_element])
        )
        await self._session.execute(query)
        await self._session.commit()

    async def update(self, update_fields: dict[str, Any], **filter_by) -> None:
        """Обновляет существующие записи в базе данных.

        Args:
        ----
            update_fields (dict): Словарь полей и их новых значений.
            filter_by: Произвольное количество именованных аргументов для фильтрации.

        """
        query = sa.update(self.model).values(**update_fields).filter_by(**filter_by)
        await self._session.execute(query)
        await self._session.commit()

    async def delete(self, **filter_by) -> None:
        """Удаляет записи, соответствующие заданным фильтрам.

        Args:
        ----
            filter_by: Произвольное количество именованных аргументов для фильтрации.

        """
        query = sa.delete(self.model).filter_by(**filter_by)
        await self._session.execute(query)
        await self._session.commit()
