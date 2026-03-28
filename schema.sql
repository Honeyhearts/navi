PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
    telegram_id   INTEGER PRIMARY KEY,
    name          TEXT,
    life_context  TEXT,
    pain_point    TEXT,
    onboard_step  INTEGER DEFAULT 0,
    referral_code TEXT UNIQUE,
    referred_by   TEXT,
    first_msg_at  TEXT,
    msg_count     INTEGER DEFAULT 0,
    summary_sent  INTEGER DEFAULT 0,
    morning_sent  INTEGER DEFAULT 0,
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id   INTEGER REFERENCES users(telegram_id),
    role          TEXT NOT NULL,
    content       TEXT NOT NULL,
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS analytics (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    event         TEXT NOT NULL,
    telegram_id   INTEGER,
    data          TEXT,
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(telegram_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event);
