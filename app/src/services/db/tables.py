from uuid import uuid4

from sqlalchemy import UUID, BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.src.services.db.base import Base


class ShippingCart(Base):
    __tablename__ = "shipping_cart"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    tool_id: Mapped[str] = mapped_column(ForeignKey("tools.id", ondelete="CASCADE"), primary_key=True)
    amount: Mapped[int] = mapped_column(default=1)

    tool: Mapped["Tool"] = relationship(lazy="selectin")


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(30))
    specifications: Mapped[str]
    price: Mapped[int]
    photo: Mapped[str]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    id_tg: Mapped[int] = mapped_column(BigInteger())
    type_executor: Mapped[str] = mapped_column(String(100))
    number_kp: Mapped[int]
    kp_tpl: Mapped[str] = mapped_column(String(255))
    number_order: Mapped[int]
    is_provider: Mapped[bool]
    country: Mapped[str] = mapped_column(String(255))

    tools: Mapped[list["ShippingCart"]] = relationship(lazy="raise")

