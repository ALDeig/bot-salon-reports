class BadAnswerTypeError(Exception):
    """Ответ в неверном формате."""


class ReportInitError(Exception):
    """Отчет не инициализирован или не удалось инициализировать."""


class ReportNotFoundError(Exception):
    """Отчет не найден."""
