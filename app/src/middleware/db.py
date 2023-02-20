from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_factory = session_factory 

    async def __call__(self, handler, event: TelegramObject, data: dict):
        session_flag = get_flag(data, "session")
        if not session_flag:
            return await handler(event, data)
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)

