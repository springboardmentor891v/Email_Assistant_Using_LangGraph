import sqlite3
from datetime import datetime

DB_PATH = "email_memory.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_memory():
    conn = get_conn()
    cur = conn.cursor()
    # 1. Ensure table exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS email_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT, subject TEXT, thread_id TEXT, 
        action TEXT, reply TEXT, created_at TEXT
    )""")
    
    # 2. FIX: Add 'reply' column to your PREVIOUSLY created table if missing
    try:
        cur.execute("ALTER TABLE email_memory ADD COLUMN reply TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists, do nothing
        
    conn.commit()
    conn.close()

def save_email_memory(sender, subject, thread_id, action, reply=""):
    conn = get_conn()
    cur = conn.cursor()
    clean_sender = sender.split('<')[-1].replace('>', '').strip() if '<' in sender else sender
    cur.execute("""
    INSERT INTO email_memory (sender, subject, thread_id, action, reply, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (clean_sender, subject, thread_id, action, reply, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_sender_history(sender, limit=3):
    conn = get_conn()
    cur = conn.cursor()
    clean_sender = sender.split('<')[-1].replace('>', '').strip() if '<' in sender else sender
    # We fetch everything so we can index safely
    cur.execute("""
    SELECT action, created_at, reply FROM email_memory 
    WHERE sender LIKE ? ORDER BY created_at DESC LIMIT ?
    """, (f"%{clean_sender}%", limit))
    rows = cur.fetchall()
    conn.close()
    return rows