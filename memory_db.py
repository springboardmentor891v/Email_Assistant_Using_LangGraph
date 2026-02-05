import sqlite3

DB_NAME = "agent_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS processed_emails (
        email_id TEXT PRIMARY KEY,
        sender TEXT,
        subject TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS meetings (
        email_id TEXT,
        date TEXT,
        time TEXT,
        duration INTEGER,
        status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()


def mark_processed(email_id, sender, subject):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT OR IGNORE INTO processed_emails VALUES (?, ?, ?)",
                 (email_id, sender, subject))
    conn.commit()
    conn.close()


def has_processed(email_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.execute("SELECT 1 FROM processed_emails WHERE email_id=?", (email_id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def save_meeting(email_id, date, time, duration, status):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO meetings VALUES (?, ?, ?, ?, ?)",
                 (email_id, date, time, duration, status))
    conn.commit()
    conn.close()


def save_preference(key, value):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT OR REPLACE INTO user_preferences VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def get_preference(key):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.execute("SELECT value FROM user_preferences WHERE key=?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
