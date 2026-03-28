import sqlite3
import json
import os
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "navi.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_conn()
    schema = Path("schema.sql").read_text()
    conn.executescript(schema)
    conn.close()

def get_user(telegram_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(telegram_id: int, referral_code: str, referred_by: str = None):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (telegram_id, referral_code, referred_by, first_msg_at) VALUES (?, ?, ?, datetime('now'))",
        (telegram_id, referral_code, referred_by)
    )
    conn.commit()
    conn.close()

def update_user(telegram_id: int, **kwargs):
    conn = get_conn()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [telegram_id]
    conn.execute(f"UPDATE users SET {sets} WHERE telegram_id = ?", vals)
    conn.commit()
    conn.close()

def increment_msg_count(telegram_id: int):
    conn = get_conn()
    conn.execute("UPDATE users SET msg_count = msg_count + 1 WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()

def save_message(telegram_id: int, role: str, content: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO messages (telegram_id, role, content) VALUES (?, ?, ?)",
        (telegram_id, role, content)
    )
    conn.commit()
    conn.close()

def get_recent_messages(telegram_id: int, limit: int = 20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE telegram_id = ? ORDER BY id DESC LIMIT ?",
        (telegram_id, limit)
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

def get_users_from_yesterday():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM users WHERE first_msg_at >= datetime('now', '-1 day') AND morning_sent = 0 AND msg_count >= 1"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_users_for_followup(min_messages: int = 1):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users WHERE msg_count >= ?", (min_messages,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_event(event: str, telegram_id: int = None, data: dict = None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO analytics (event, telegram_id, data) VALUES (?, ?, ?)",
        (event, telegram_id, json.dumps(data) if data else None)
    )
    conn.commit()
    conn.close()

def get_dashboard_stats():
    conn = get_conn()
    stats = {}
    stats["total_users"] = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    stats["total_messages"] = conn.execute("SELECT COUNT(*) FROM messages WHERE role = 'user'").fetchone()[0]
    stats["active_conversations"] = conn.execute(
        "SELECT COUNT(*) FROM users WHERE msg_count >= 3"
    ).fetchone()[0]
    stats["avg_messages"] = conn.execute(
        "SELECT COALESCE(AVG(msg_count), 0) FROM users WHERE msg_count > 0"
    ).fetchone()[0]
    stats["referrals"] = conn.execute(
        "SELECT COUNT(*) FROM users WHERE referred_by IS NOT NULL"
    ).fetchone()[0]
    stats["summaries_sent"] = conn.execute(
        "SELECT COUNT(*) FROM users WHERE summary_sent = 1"
    ).fetchone()[0]

    life_contexts = conn.execute(
        "SELECT life_context, COUNT(*) as cnt FROM users WHERE life_context IS NOT NULL GROUP BY life_context ORDER BY cnt DESC"
    ).fetchall()
    stats["archetypes"] = [{"context": r[0], "count": r[1]} for r in life_contexts]

    top_requests = conn.execute(
        "SELECT data, COUNT(*) as cnt FROM analytics WHERE event = 'user_request_category' GROUP BY data ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    stats["top_requests"] = [{"category": r[0], "count": r[1]} for r in top_requests]

    conn.close()
    return stats
