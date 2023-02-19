import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from app.src.services.db.base import Base


class User(Base):
    __tablename__ = "user"
    id = sa.Column(sa.BigInteger, primary_key=True, index=True)
    name = sa.Column(sa.String)

