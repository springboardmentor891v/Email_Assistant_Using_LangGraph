import sqlite3

DB_PATH = "data/email_final.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        subject TEXT,
        body TEXT,
        reply TEXT,
        politeness_score REAL
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
def save_email_interaction(
    sender: str,
    subject: str,
    body: str,
    ai_reply: str,
    final_reply: str,
    decision: str
):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO emails (sender, subject, body, reply, politeness_score)
    VALUES (?, ?, ?, ?, ?)
""", (sender, subject, body, final_reply, None))

    email_id = cur.lastrowid

    conn.commit()
    conn.close()
    return email_id
def get_recent_human_edits(limit=5):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT reply
        FROM emails
        WHERE reply IS NOT NULL
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    return [row[0] for row in rows]
def update_politeness_score(email_id: int, score: float):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE emails
        SET politeness_score = ?
        WHERE id = ?
    """, (score, email_id))

    conn.commit()
    conn.close()
