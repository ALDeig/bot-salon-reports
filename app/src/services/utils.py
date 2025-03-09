from datetime import datetime
from zoneinfo import ZoneInfo

TZ = "Europe/Moscow"


def get_time() -> datetime:
    return datetime.now(ZoneInfo(TZ))
