import socket
import threading
import secrets
from config import HOST, PORT
from database import init_db, register_user, get_user, save_message
from encryption import encrypt_message, hash_password, verify_password

clients = {}
rooms = {}
lock = threading.Lock()


def broadcast(message, room):
    with lock:
        for username, sock in list(clients.items()):
            if rooms.get(username) == room:
                try:
                    sock.send((message + "\n").encode())
                except:
                    pass


def handle_client(conn, addr):
    username = None
    room = None

    try:
        conn.send("Welcome to localcrypt!\n1. Register\n2. Login\nChoice: ".encode())
        choice = conn.recv(1024).decode().strip()

        # REGISTER
        if choice == "1":
            conn.send("Username: ".encode())
            username = conn.recv(1024).decode().strip()

            conn.send("Password: ".encode())
            password = conn.recv(1024).decode().strip()

            hashed = hash_password(password)
            api_key = secrets.token_hex(16)

            if register_user(username, hashed, api_key):
                conn.send("Registered successfully.\n".encode())
            else:
                conn.send("Username already exists.\n".encode())
                conn.close()
                return

        # LOGIN
        conn.send("Username: ".encode())
        username = conn.recv(1024).decode().strip()

        conn.send("Password: ".encode())
        password = conn.recv(1024).decode().strip()

        user = get_user(username)
        if not user or not verify_password(password, user[2]):
            conn.send("Invalid credentials.\n".encode())
            conn.close()
            return

        conn.send(f"Logged in! Welcome {username}\nRoom name: ".encode())
        room = conn.recv(1024).decode().strip()

        with lock:
            clients[username] = conn
            rooms[username] = room

        broadcast(f"[+] {username} joined {room}", room)
        conn.send("Connected. Use /online or /quit\n".encode())

        # MAIN LOOP
        while True:
            data = conn.recv(4096).decode().strip()
            if not data:
                break

            print("RECEIVED:", data)

            if data == "/quit":
                break

            elif data == "/online":
                with lock:
                    online = [u for u, r in rooms.items() if r == room]
                conn.send((f"Online: {', '.join(online)}\n").encode())

            else:
                encrypted = encrypt_message(data)
                save_message(username, room, encrypted)
                broadcast(f"{username}: {data}", room)

    except Exception as e:
        print("Error:", e)

    finally:
        with lock:
            if username in clients:
                del clients[username]
            if username in rooms:
                del rooms[username]

        if room and username:
            broadcast(f"[-] {username} left {room}", room)

        conn.close()


def start_server():
    init_db()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"[*] Server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print(f"[+] Connection from {addr}")
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()