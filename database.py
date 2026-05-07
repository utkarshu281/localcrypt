import sqlite3
from config import DB_FILE

def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        api_key TEXT NOT NULL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        room TEXT NOT NULL,
        content TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        private INTEGER DEFAULT 0
    )""")
    con.commit()
    con.close()

def register_user(username, password_hash, api_key):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, api_key) VALUES (?,?,?)",
            (username, password_hash, api_key)
        )
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        con.close()

def get_user(username):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    con.close()
    return result

def get_user_by_api_key(api_key):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
    result = cur.fetchone()
    con.close()
    return result

def save_message(username, room, content, private=0):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO messages (username, room, content, private) VALUES (?,?,?,?)",
        (username, room, content, private)
    )
    con.commit()
    con.close()

# ✅ FIXED FUNCTION
def get_messages(room, limit=50):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    cur.execute("""
        SELECT username, content, timestamp
        FROM messages
        WHERE room = ?
        ORDER BY id ASC
    """, (room,))

    result = cur.fetchall()
    con.close()

    return result[-limit:]  # last N messages in correct order

def get_all_users():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT username FROM users")
    result = cur.fetchall()
    con.close()
    return [r[0] for r in result]