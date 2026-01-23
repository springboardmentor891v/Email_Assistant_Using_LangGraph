import sqlite3
from datetime import datetime
import json

class MemoryStore:
    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            intent TEXT,
            content TEXT
        )
        """)

    def save(self, intent, content):
        # Convert dict to JSON string for SQLite
        content_str = json.dumps(content) if isinstance(content, dict) else str(content)
        self.conn.execute(
            "INSERT INTO interactions VALUES (NULL, ?, ?, ?)",
            (datetime.utcnow().isoformat(), intent, content_str)
        )
        self.conn.commit()

    def fetch_recent(self, limit=5):
        cursor = self.conn.execute(
            "SELECT intent, content FROM interactions ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return cursor.fetchall()
