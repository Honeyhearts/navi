import logging
import db
import llm

logger = logging.getLogger(__name__)

SUMMARY_THRESHOLD = 5

async def maybe_send_summary(bot, telegram_id: int):
    user = db.get_user(telegram_id)
    if not user or user["summary_sent"] or user["msg_count"] < SUMMARY_THRESHOLD:
        return

    recent = db.get_recent_messages(telegram_id, limit=20)
    if not recent:
        return

    try:
        profile = llm.generate_summary_card(user, recent)
        await bot.send_message(chat_id=telegram_id, text=profile)
        db.update_user(telegram_id, summary_sent=1)
        db.log_event("summary_generated", telegram_id)
        logger.info(f"Summary card sent to user {telegram_id}")
    except Exception as e:
        logger.error(f"Failed to generate summary for {telegram_id}: {e}")
