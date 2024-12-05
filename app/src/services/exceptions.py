class BadAnswerTypeError(Exception):
    """Ответ в неверном формате."""


class ReportInitError(Exception):
    """Отчет не инициализирован или не удалось инициализировать."""

    def __init__(self, message: str = "Не удалось инициализировать отчет") -> None:
        self.message = message
        super().__init__(self.message)


class ReportNotFoundError(Exception):
    """Отчет не найден."""


class ReportIsClosedError(Exception):
    """Отчет закрыт."""
