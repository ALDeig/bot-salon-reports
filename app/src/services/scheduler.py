from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.src.services.db.base import session_factory
from app.src.services.db.dao.dao import ReportDao


async def delete_old_reports():
    old_date = datetime.now() - timedelta(7)  # noqa: DTZ005
    async with session_factory() as session:
        await ReportDao(session).delete_old_reports(old_date)


def create_scheduler_tasks() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(delete_old_reports, "cron", hour=7)
    return scheduler
