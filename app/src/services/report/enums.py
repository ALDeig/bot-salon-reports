from enum import Enum


class AnswerType(int, Enum):
    """Типы ответа."""

    Text = 1
    Photo = 2
    Video = 3
