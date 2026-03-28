import os
import logging
from datetime import datetime, timezone, timedelta
from telegram import Update, ChatAction
from telegram.ext import ContextTypes

import db
import llm
import alerts
import referrals
import summary

logger = logging.getLogger(__name__)

RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_USER", "50"))
STALE_SECONDS = int(os.getenv("STALE_MESSAGE_SECONDS", "300"))
FOUNDER_CHAT_ID = os.getenv("FOUNDER_CHAT_ID")

ONBOARDING_QUESTIONS = [
    "First, what's your name?",
    "Nice to meet you, {name}! What best describes your day-to-day: running a business, creative work, family + career, fitness, studying, or something else?",
    "Got it. What's the one thing that keeps falling through the cracks in your week? The thing you keep meaning to do but never get to.",
]

PRIVACY_NOTICE = "Quick note: our conversations during this test flight are logged to help us build the best product. No data is shared with third parties."


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    start_param = context.args[0] if context.args else None

    referred_by = referrals.extract_referral_from_start(start_param)
    code = referrals.generate_code()
    db.create_user(telegram_id, referral_code=code, referred_by=referred_by)

    if referred_by:
        db.log_event("referral_arrived", telegram_id, {"code": referred_by})

    welcome = (
        f"Welcome to the Navi test flight! I'm your AI navigator.\n\n"
        f"{PRIVACY_NOTICE}\n\n"
        f"{ONBOARDING_QUESTIONS[0]}"
    )
    await update.message.reply_text(welcome)
    db.update_user(telegram_id, onboard_step=1)
    db.log_event("onboarding_started", telegram_id)


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != FOUNDER_CHAT_ID:
        return

    stats = db.get_dashboard_stats()
    msg = (
        f"NAVI STATUS\n"
        f"━━━━━━━━━━━\n"
        f"Users: {stats['total_users']}\n"
        f"Messages: {stats['total_messages']}\n"
        f"Active (3+ msgs): {stats['active_conversations']}\n"
        f"Avg msgs/user: {stats['avg_messages']:.1f}\n"
        f"Referrals: {stats['referrals']}\n"
        f"Summaries sent: {stats['summaries_sent']}\n"
    )
    if stats["archetypes"]:
        msg += "\nArchetypes:\n"
        for a in stats["archetypes"]:
            msg += f"  {a['context']}: {a['count']}\n"

    await update.message.reply_text(msg)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return

    telegram_id = update.effective_user.id
    msg_time = update.message.date

    # Skip stale messages (after internet outage)
    if msg_time:
        age = (datetime.now(timezone.utc) - msg_time).total_seconds()
        if age > STALE_SECONDS:
            logger.info(f"Skipping stale message from {telegram_id}, age={age:.0f}s")
            return

    # Handle non-text input
    if not update.message.text:
        media_type = "something"
        if update.message.photo:
            media_type = "a photo"
            reply = (
                f"I can see you sent {media_type}! In the full version, Navi can analyze "
                f"images, read documents, identify products, and extract text. In test "
                f"flight mode I'm text-only. Tell me about what you sent?"
            )
        elif update.message.voice or update.message.audio:
            reply = (
                "Voice message received! Full Navi will understand voice natively. "
                "For now, type what you wanted to say and I'm on it."
            )
        elif update.message.sticker:
            reply = "Ha! I appreciate the energy. I can't process stickers yet, but what's on your mind?"
        elif update.message.document:
            reply = (
                "I see a file! Full Navi can read documents, spreadsheets, and PDFs. "
                "In test flight mode, tell me what's in it and I'll work with that."
            )
        else:
            reply = "I got that, but I can only work with text messages during this test flight. What's on your mind?"

        await update.message.reply_text(reply)
        db.log_event("non_text_input", telegram_id, {"type": media_type})
        return

    text = update.message.text.strip()
    user = db.get_user(telegram_id)

    # New user who didn't use /start
    if not user:
        code = referrals.generate_code()
        db.create_user(telegram_id, referral_code=code)
        user = db.get_user(telegram_id)
        welcome = (
            f"Hey there! Welcome to the Navi test flight.\n\n"
            f"{PRIVACY_NOTICE}\n\n"
            f"{ONBOARDING_QUESTIONS[0]}"
        )
        await update.message.reply_text(welcome)
        db.update_user(telegram_id, onboard_step=1)
        return

    # Onboarding flow
    step = user.get("onboard_step", 0)
    if step == 1:
        db.update_user(telegram_id, name=text, onboard_step=2)
        question = ONBOARDING_QUESTIONS[1].format(name=text)
        await update.message.reply_text(question)
        return

    if step == 2:
        db.update_user(telegram_id, life_context=text, onboard_step=3)
        await update.message.reply_text(ONBOARDING_QUESTIONS[2])
        return

    if step == 3:
        db.update_user(telegram_id, pain_point=text, onboard_step=4)
        db.log_event("onboarding_complete", telegram_id)

        # Generate personalized first response
        user = db.get_user(telegram_id)
        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            intro_messages = llm.build_chat_messages(user, [
                {"role": "user", "content": f"I just told you my name is {user['name']}, I'm into {user['life_context']}, and the thing falling through the cracks is: {user['pain_point']}. What would you do for me?"}
            ])
            response = llm.call_llm(intro_messages)
            db.save_message(telegram_id, "user", text)
            db.save_message(telegram_id, "assistant", response)
            db.increment_msg_count(telegram_id)
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"LLM error during onboarding completion: {e}")
            await alerts.alert_founder(context.bot, f"LLM error for user {telegram_id}: {e}")
            await update.message.reply_text(
                "I'm having a moment. Give me a few seconds and try again?"
            )
        return

    # Rate limiting
    if user["msg_count"] >= RATE_LIMIT:
        recent = db.get_recent_messages(telegram_id, limit=10)
        recap_items = [m["content"][:80] for m in recent if m["role"] == "user"]
        recap = "\n".join(f"  - {item}" for item in recap_items[-5:])
        await update.message.reply_text(
            f"You've been exploring a lot! I'll be back tomorrow.\n\n"
            f"Here's what we talked about:\n{recap}\n\n"
            f"In the meantime, imagine all of this handled automatically. That's what full Navi does."
        )
        db.log_event("rate_limited", telegram_id)
        return

    # Regular chat
    await update.message.chat.send_action(ChatAction.TYPING)

    db.save_message(telegram_id, "user", text)
    db.increment_msg_count(telegram_id)
    recent = db.get_recent_messages(telegram_id)

    try:
        messages = llm.build_chat_messages(user, recent)
        response = llm.call_llm(messages)
        db.save_message(telegram_id, "assistant", response)
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"LLM error for {telegram_id}: {e}")
        await alerts.alert_founder(context.bot, f"LLM error for user {telegram_id}: {e}")
        await update.message.reply_text(
            "Let me think on that... I'm having a brief hiccup. Try again in a moment?"
        )
        return

    # Post-message hooks
    user = db.get_user(telegram_id)

    # Offer referral link after first real conversation (msg_count == 3)
    if user["msg_count"] == 3:
        bot_username = (await context.bot.get_me()).username
        link = referrals.build_referral_link(bot_username, user["referral_code"])
        await update.message.reply_text(
            f"Enjoying the test flight? Share it with a friend:\n{link}"
        )

    # Summary card after threshold
    await summary.maybe_send_summary(context.bot, telegram_id)
