import secrets
from typing import Optional
import db

def generate_code() -> str:
    return secrets.token_urlsafe(4)[:6].upper()

def get_or_create_referral(telegram_id: int) -> str:
    user = db.get_user(telegram_id)
    if user and user["referral_code"]:
        return user["referral_code"]
    code = generate_code()
    db.update_user(telegram_id, referral_code=code)
    return code

def build_referral_link(bot_username: str, code: str) -> str:
    return f"https://t.me/{bot_username}?start=ref_{code}"

def extract_referral_from_start(start_param: str) -> Optional[str]:
    if start_param and start_param.startswith("ref_"):
        return start_param[4:]
    return None
