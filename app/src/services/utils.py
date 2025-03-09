from datetime import datetime
from zoneinfo import ZoneInfo

TZ = "Europe/Moscow"
TZ_INFO = ZoneInfo(TZ)


def get_time() -> datetime:
    return datetime.now(TZ_INFO)
