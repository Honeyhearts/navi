import os
import logging
import asyncio
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import db
import handlers
import dashboard
import morning
import followup

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    db.init_db()
    logger.info("Database initialized")

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN not set")
        return

    app = ApplicationBuilder().token(token).build()

    # Command handlers
    app.add_handler(CommandHandler("start", handlers.handle_start))
    app.add_handler(CommandHandler("status", handlers.handle_status))

    # Message handler (text and non-text)
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handlers.handle_message))

    # Schedule cron jobs
    scheduler = AsyncIOScheduler()

    # Morning message at 8am local time
    scheduler.add_job(
        morning.send_morning_messages,
        "cron",
        hour=8,
        minute=0,
        args=[app.bot],
        id="morning_message",
    )

    # Follow-up 48 hours after conference end
    conf_end = os.getenv("CONFERENCE_END_TIME")
    if conf_end:
        from datetime import timedelta
        followup_time = datetime.fromisoformat(conf_end) + timedelta(hours=48)
        scheduler.add_job(
            followup.send_followup_messages,
            "date",
            run_date=followup_time,
            args=[app.bot],
            id="followup_message",
        )
        logger.info(f"Follow-up scheduled for {followup_time}")

    # SQLite backup every 6 hours
    scheduler.add_job(
        backup_database,
        "interval",
        hours=6,
        id="db_backup",
    )

    scheduler.start()

    # Dashboard in background thread
    dash_thread = threading.Thread(target=dashboard.run_dashboard, daemon=True)
    dash_thread.start()

    logger.info("Navi bot starting...")
    app.run_polling(drop_pending_updates=True)


def backup_database():
    import shutil
    from pathlib import Path
    src = db.DB_PATH
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = backup_dir / f"navi_{ts}.db"
    shutil.copy2(src, dst)

    # Keep only last 10 backups
    backups = sorted(backup_dir.glob("navi_*.db"), reverse=True)
    for old in backups[10:]:
        old.unlink()

    logger.info(f"Database backed up to {dst}")


if __name__ == "__main__":
    main()
