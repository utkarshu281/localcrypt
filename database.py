import sqlite3
from config import DB_FILE
def init_db():
    con=sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS USERS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        api_key TEXT NOT NULL
        )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS Messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        Room TEXT NOT NULL,
        content TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        private INTEGER
        )""")
    con.commit()
def register_usr(username,password_hash,api_key):
    con=sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("INSERT INTO USERS (username, password_hash, api_key) VALUES(?,?,?)",(username,password_hash,api_key))
    con.commit()
    
def registered_users():
    con=sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT username FROM users")
    row =cur.fetchone()
    print("First row:", row)
    con.commit()

def verify_login(username):
    con=sqlite3.connect(DB_FILE)
    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cur.fetchone()
        if result:
            print("Found user:", result)
        else:
            print("User not found")
    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        cur.close()
        con.close()
    
def save_messages(username,content,Room):
    con=sqlite3.connect(DB_FILE)
    cur=con.cursor()
    cur.execute("INSERT INTO Messages (username,content,Room) VALUES(?,?,?)",(username,content,Room)) 
    con.commit()
        
def get_messages(Room):
    con=sqlite3.connect(DB_FILE)
    cur=con.cursor()
    try:
        cur.execute("SELECT content from Messages WHERE Room = ?",(Room,))
        result = cur.fetchall()
        print(f"Messgaes for this {Room} is:",result)
    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        cur.close()
        con.close()
            
def delete_user(username):
    con=sqlite3.connect(DB_FILE)
    cur=con.cursor()
    try:
        cur.execute("DELETE FROM USERS WHERE username = ?",(username,))
        verify_login(username)
    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        con.commit()
        cur.close()
        con.close()
#this function runs first
if __name__ == "__main__":
    init_db()
    register_usr("utkarsh", "fakehash", "fakekey")
    verify_login("utkarsh")
    save_messages("utkarsh", "hello everyone", "general")
    get_messages("general")