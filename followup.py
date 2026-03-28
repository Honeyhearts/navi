import logging
import asyncio
from telegram import Bot
from telegram.error import Forbidden

import db

logger = logging.getLogger(__name__)

PRESIGNUP_URL = "https://heynavi.com"  # Update with actual domain


async def send_followup_messages(bot: Bot):
    all_users = db.get_users_for_followup(min_messages=1)
    if not all_users:
        logger.info("Follow-up cron: no users to message")
        return

    logger.info(f"Follow-up cron: sending to {len(all_users)} users")

    for user in all_users:
        telegram_id = user["telegram_id"]
        name = user.get("name", "there")

        if user["msg_count"] >= 3:
            message = (
                f"Hey {name}! Thanks for test flying Navi. "
                f"We're building the real thing. Want to be first in line?\n\n"
                f"{PRESIGNUP_URL}\n\n"
                f"The full Navi will actually do the things we talked about. "
                f"Every morning, on your schedule, with your priorities."
            )
        else:
            message = (
                f"Hey {name}! Hope you enjoyed the Navi preview. "
                f"We're building something special.\n\n"
                f"Sign up to be first in line: {PRESIGNUP_URL}"
            )

        try:
            await bot.send_message(chat_id=telegram_id, text=message)
            db.log_event("followup_sent", telegram_id)
            logger.info(f"Follow-up sent to {telegram_id}")
        except Forbidden:
            logger.info(f"User {telegram_id} blocked bot, skipping")
        except Exception as e:
            logger.error(f"Failed to send follow-up to {telegram_id}: {e}")

        await asyncio.sleep(1)
