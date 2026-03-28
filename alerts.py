import os
import logging

logger = logging.getLogger(__name__)

FOUNDER_CHAT_ID = os.getenv("FOUNDER_CHAT_ID")

async def alert_founder(bot, message: str):
    if not FOUNDER_CHAT_ID:
        logger.warning("FOUNDER_CHAT_ID not set, cannot send alert")
        return
    try:
        await bot.send_message(
            chat_id=int(FOUNDER_CHAT_ID),
            text=f"🚨 NAVI ALERT\n\n{message}"
        )
    except Exception as e:
        logger.error(f"Failed to alert founder: {e}")
