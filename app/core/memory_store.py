
import sqlite3
from datetime import datetime

DB_PATH = "email_memory.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_memory():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS email_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        subject TEXT,
        thread_id TEXT,
        action TEXT,
        reply TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_email_memory(sender, subject, thread_id, action, reply=""):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO email_memory
    (sender, subject, thread_id, action, reply, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        sender,
        subject,
        thread_id,
        action,
        reply,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

def get_sender_history(sender, limit=3):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT action, created_at
    FROM email_memory
    WHERE sender = ?
    ORDER BY created_at DESC
    LIMIT ?
    """, (sender, limit))

    rows = cur.fetchall()
    conn.close()
    return rows
