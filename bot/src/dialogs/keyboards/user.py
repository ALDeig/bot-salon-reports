from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


kb_create_poll = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Добавить опрос", callback_data="add_poll")]]
)
