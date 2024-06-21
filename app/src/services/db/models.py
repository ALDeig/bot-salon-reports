from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.src.services.db.base import Base
from app.src.services.report.enums import AnswerType


class MUser(Base):
    """Пользователи."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    full_name: Mapped[str]
    username: Mapped[str] = mapped_column(Text, nullable=True)


class MSalon(Base):
    """Салоны."""

    __tablename__ = "salons"

    id: Mapped[int] = mapped_column(
        Integer, init=False, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100))
    shift_is_close: Mapped[bool] = mapped_column(Boolean, default=True)


class MReport(Base, kw_only=True):
    """Отчеты."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(
        Integer, init=False, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    salon_id: Mapped[int] = mapped_column(ForeignKey("salons.id"))
    created: Mapped[datetime] = mapped_column(DateTime, default_factory=datetime.now)
    closed: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    questions: Mapped[list["MQuestion"]] = relationship(
        lazy="selectin", cascade="all, delete", init=False
    )


class MQuestion(Base):
    """Вопросы для конкретного отчета."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(
        Integer, init=False, primary_key=True, autoincrement=True
    )
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    type: Mapped[AnswerType] = mapped_column(Integer)
    is_require: Mapped[bool] = mapped_column(Boolean)

    answer: Mapped["MAnswer"] = relationship(
        lazy="selectin", cascade="all, delete", init=False
    )


class MAnswer(Base):
    """Ответы."""

    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True
    )
    data: Mapped[str] = mapped_column(Text)
