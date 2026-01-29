import sqlite3

DB_PATH = "data/email_final.db"

def show_dashboard():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM emails")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM emails WHERE politeness_score >= 8")
    auto = cur.fetchone()[0]

    cur.execute("SELECT AVG(politeness_score) FROM emails")
    avg = cur.fetchone()[0]

    conn.close()

    print("\n📊 EMAIL AGENT DASHBOARD\n")
    print("Total emails handled:", total)
    print("Auto-approved emails:", auto)
    print("Average politeness score:", round(avg or 0, 2))

if __name__ == "__main__":
    show_dashboard()
