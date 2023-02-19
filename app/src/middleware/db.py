from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(self, handler, event: TelegramObject, data: dict):
        db = get_flag(data, "db")
        if not db:
            return await handler(event, data)
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)

