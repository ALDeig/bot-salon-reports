from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from fastapi import FastAPI, Request

from config import config_load


app = FastAPI()


def get_bot():
    config = config_load()
    session = AiohttpSession()
    bot_settings = {"session": session, "parse_mode": "HTML"}
    bot = Bot(token=config.tg.token, **bot_settings)
    return bot, session


@app.post("/")
async def send_message():
    bot, session = get_bot()
    await bot.send_message(
        chat_id=381428187,
        text="hello, this message sent from fast api app"
    )
    await session.close()


