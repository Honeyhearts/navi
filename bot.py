import os
import logging
import threading
from datetime import datetime, time, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

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


async def morning_job(context: ContextTypes.DEFAULT_TYPE):
    await morning.send_morning_messages(context.bot)


async def followup_job(context: ContextTypes.DEFAULT_TYPE):
    await followup.send_followup_messages(context.bot)


async def backup_job(context: ContextTypes.DEFAULT_TYPE):
    backup_database()


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

    # Message handler
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handlers.handle_message))

    # Morning message at 8am local time
    app.job_queue.run_daily(
        morning_job,
        time=time(8, 0, tzinfo=timezone.utc),
        name="morning_message",
    )

    # Follow-up 48 hours after conference end
    conf_end = os.getenv("CONFERENCE_END_TIME")
    if conf_end:
        followup_time = datetime.fromisoformat(conf_end).replace(tzinfo=timezone.utc) + timedelta(hours=48)
        if followup_time > datetime.now(timezone.utc):
            app.job_queue.run_once(
                followup_job,
                when=followup_time,
                name="followup_message",
            )
            logger.info(f"Follow-up scheduled for {followup_time}")

    # SQLite backup every 6 hours
    app.job_queue.run_repeating(
        backup_job,
        interval=6 * 3600,
        first=6 * 3600,
        name="db_backup",
    )

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
