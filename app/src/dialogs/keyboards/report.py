from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.src.services.db.models import MQuestion, MSalon

kb_skip = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Пропустить", callback_data="skip")]]
)


def kb_salons(salons: Sequence[MSalon]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for salon in salons:
        builder.add(InlineKeyboardButton(text=salon.name, callback_data=str(salon.id)))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


IS_REQUIRE_EMOJI = {True: "❗️", False: ""}
IS_DONE_EMOJI = {True: "✅", False: ""}


def kb_questions(questions: Sequence[MQuestion]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for question in questions:
        text, callback_data = _question_button_data(question)
        builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    builder.add(
        InlineKeyboardButton(
            text="Закрыть смену", callback_data=f"finish:{questions[0].report_id}"
        )
    )
    builder.adjust(2)
    return builder.as_markup()


def _question_button_data(question: MQuestion) -> tuple[str, str]:
    text = (
        f"{IS_DONE_EMOJI[bool(question.answer)]}"
        f"{IS_REQUIRE_EMOJI[question.is_require]}{question.text}"
    )
    prefix = "" if question.answer else "ask:"
    callback_data = f"{prefix}{question.id}:{question.report_id}"
    return text, callback_data
