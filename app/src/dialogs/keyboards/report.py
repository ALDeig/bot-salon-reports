from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

kb_skip = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Пропустить", callback_data="skip")]]
)


def kb_salons(*salons: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for salon in salons:
        builder.add(KeyboardButton(text=salon))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
