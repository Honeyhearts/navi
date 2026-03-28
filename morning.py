import logging
import asyncio
from telegram import Bot
from telegram.error import Forbidden

import db
import llm

logger = logging.getLogger(__name__)


async def send_morning_messages(bot: Bot):
    users = db.get_users_from_yesterday()
    if not users:
        logger.info("Morning cron: no users from yesterday")
        return

    logger.info(f"Morning cron: sending to {len(users)} users")

    for user in users:
        telegram_id = user["telegram_id"]
        try:
            recent = db.get_recent_messages(telegram_id, limit=20)
            if not recent:
                continue

            message = llm.generate_morning_message(user, recent)
            await bot.send_message(chat_id=telegram_id, text=message)
            db.update_user(telegram_id, morning_sent=1)
            db.log_event("morning_sent", telegram_id)
            logger.info(f"Morning message sent to {telegram_id}")

        except Forbidden:
            logger.info(f"User {telegram_id} blocked the bot, skipping")
            db.log_event("user_blocked", telegram_id)

        except Exception as e:
            logger.error(f"Failed to send morning message to {telegram_id}: {e}")

        await asyncio.sleep(1)  # Don't spam Telegram API
