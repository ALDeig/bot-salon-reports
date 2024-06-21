from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.src.services.db.models import MReport


def kb_select_report(reports: Sequence[MReport]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for report in reports:
        builder.add(
            InlineKeyboardButton(
                text=report.created.strftime("%d.%m.%y"), callback_data=str(report.id)
            )
        )
    builder.adjust(2)
    return builder.as_markup()
