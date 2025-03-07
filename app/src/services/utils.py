from datetime import datetime
from zoneinfo import ZoneInfo

tz = ZoneInfo("Europe/Moscow")


def get_time() -> datetime:
    return datetime.now(tz)
