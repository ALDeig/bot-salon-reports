from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

kb_skip = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Пропустить", callback_data="skip")]]
)
