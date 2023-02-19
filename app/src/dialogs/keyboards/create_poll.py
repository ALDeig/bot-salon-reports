from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


kb_show_total_result = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Посмотреть результат", callback_data="show_result")]]
)
