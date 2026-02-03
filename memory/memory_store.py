# memory/memory_store.py
import sqlite3

DB_NAME = "memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_preference(key, value):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO preferences VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()


def get_preference(key):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT value FROM preferences WHERE key = ?",
        (key,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def save_feedback(key, value):
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()

def get_feedback(key):
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT value FROM preferences WHERE key = ?",
        (key,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
