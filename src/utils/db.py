import sqlite3

conn = sqlite3.connect("cyai.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tips (
    user_id TEXT,
    tip TEXT
)
""")
conn.commit()

def store_tip(user_id, tip):
    cursor.execute("INSERT INTO tips (user_id, tip) VALUES (?, ?)", (user_id, tip))
    conn.commit()

def get_tips_for_user(user_id):
    cursor.execute("SELECT tip FROM tips WHERE user_id = ?", (user_id,))
    return [row[0] for row in cursor.fetchall()]
