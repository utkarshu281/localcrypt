# SecureChat
Real-time encrypted CLI chat — TCP sockets, SQLite, Fernet AES, Flask REST API

Multiple users connect over a local network, messages are encrypted before storage, and a REST API exposes chat history and stats. Built in Python, no external servers required.

## Features

- Register and login with hashed passwords (bcrypt)
- Create or join named chat rooms
- Real-time broadcast messaging via TCP sockets
- Private messaging with `/msg username`
- All messages encrypted at rest (Fernet AES-128)
- Chat history via REST API with API key authentication
- Works across machines on the same Wi-Fi network

---

## Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Real-time messaging | Python `socket` | TCP client-server communication |
| Concurrency | `threading` | One thread per connected client |
| Database | `sqlite3` (built-in) | Store users and messages |
| Message encryption | `cryptography` (Fernet) | Encrypt all messages before storage |
| Password security | `bcrypt` | Hash passwords, never store plain text |
| REST API | `Flask` | Async access to history and stats |
| HTTP client | `requests` | Client-side API calls |

---

## Project Structure

```
securechat/
├── server.py        # Socket server, one thread per client, broadcast logic
├── client.py        # Terminal UI, send thread, receive thread
├── database.py      # All SQLite operations (only file that touches the DB)
├── encryption.py    # Fernet encrypt/decrypt + bcrypt hash/verify
├── api.py           # Flask REST API, runs as background thread
├── config.py        # HOST, PORT, DB path, key path
├── requirements.txt
└── README.md
```

---

## Setup

```bash
git clone https://github.com/yourusername/securechat
cd securechat
pip install -r requirements.txt
```

**Requirements:**
```
cryptography
bcrypt
flask
requests
```

---

## Usage

### 1. Start the server

Run this once on your machine:

```bash
python server.py
```

Output:
```
[*] Server started on 127.0.0.1:5555
[*] API running on 127.0.0.1:5000
[*] Waiting for connections...
```

### 2. Connect as a client

Run on any machine on the same network:

```bash
python client.py
```

On first run, choose **Register**. After that, choose **Login**.

```
=== Welcome to SecureChat ===
1. Register
2. Login
3. Exit
Choice:
```

### 3. Join or create a room

```
=== Room Menu ===
1. Create room
2. Join room
Choice:
Room name: general
```

### 4. Start chatting

```
=== general ===
[+] utkarsh joined the room
utkarsh: hello everyone
john: hey!
```

---

## Commands

| Command | Action |
|---------|--------|
| `/msg username text` | Send a private message |
| `/online` | List currently connected users |
| `/history` | Fetch last 50 messages via API |
| `/quit` | Disconnect from the room |

---

## REST API

All endpoints require the `X-API-Key` header. Your API key is shown once at login.

```
GET  /messages        Last 50 messages (decrypted JSON)
GET  /users           List of registered usernames
POST /send            Send a message via HTTP (no socket needed)
GET  /stats           Total message count, active users
```

**Example:**
```bash
curl -H "X-API-Key: your_key_here" http://localhost:5000/messages
```

**Response:**
```json
[
  { "sender": "utkarsh", "content": "hello everyone", "timestamp": "2026-03-17 10:00:00" },
  { "sender": "john",    "content": "hey!",            "timestamp": "2026-03-17 10:00:05" }
]
```

---

## Running on a Local Network

To let teammates connect from their machines:

**Step 1 — Find your local IP:**
```bash
# Windows
ipconfig
# Look for: IPv4 Address . . . 192.168.x.x

# Linux
ip a
# Look for: inet 192.168.x.x
```

**Step 2 — Update config.py:**
```python
HOST = "192.168.1.5"   # replace with your actual local IP
```

**Step 3 — Others run client.py** with the same HOST set in their config.py. Everyone must be on the same Wi-Fi network.

---

## How It Works

```
Client A types message
    │
    ▼
Socket → Server receives
    │
    ├─► Fernet encrypt → store in SQLite (encrypted blob)
    │
    ├─► Fernet decrypt → broadcast plain text to all clients
    │
    ▼
Client B, C, D print message instantly
```

**Passwords** are hashed with bcrypt before storage. The original password is never saved anywhere.

**Messages** are encrypted with Fernet (AES-128-CBC) before being written to the database. Even if someone opens the `.db` file directly, all message content is unreadable.

**API keys** are random strings generated at login, stored in the users table, and required for every REST API call.

---

## Security Notes

- Passwords: bcrypt hashed, never stored plain
- Messages: AES-128 encrypted at rest via Fernet
- API: key-based authentication on all endpoints
- In-transit: plain text over local network (TLS not implemented — out of scope for this project)

---

## What We Learned

- TCP socket programming — bind, listen, accept, connect lifecycle
- Threading for concurrent client handling without blocking
- SQLite schema design and parameterized queries (no SQL injection)
- Symmetric encryption with Fernet (AES-128-CBC + HMAC)
- Password security — why you never store plain text, how bcrypt works
- Building a REST API with Flask alongside a socket server
- Local network communication across real machines

---

## Environment

- Python 3.10+
- Tested on Windows 10 and Ubuntu 22.04
- No external services — runs entirely offline on local network

---

*College team project — CSE Semester 4, 2026*
