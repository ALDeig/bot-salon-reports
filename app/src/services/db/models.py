from sqlalchemy import JSON, BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.src.services.db.base import Base


class User(Base):
    """Пользователи."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    full_name: Mapped[str]
    username: Mapped[str] = mapped_column(Text, nullable=True)


class Salon(Base):
    """Салоны."""

    __tablename__ = "salons"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))


class Report(Base):
    """Отчеты."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(ForeignKey("salons.id"), primary_key=True)
    answers: Mapped[list[dict]] = mapped_column(JSON)
