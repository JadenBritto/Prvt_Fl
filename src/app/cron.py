from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from app.settings import get_settings

settings = get_settings()

scheduler = AsyncIOScheduler(jobstores={"default": SQLAlchemyJobStore(url=settings.db.axentra_db_url_sync)})

def start_scheduler():
    scheduler.start()
    print("🚀 Async scheduler started without any cron jobs.")
