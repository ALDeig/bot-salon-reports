import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.services.db.tables import User


async def add_user(session: AsyncSession, user_id: int, name: str, role: str):
    user = User(id=user_id, name=name, role=role)
    session.add(user)
    await session.commit()

