from flask import Flask, jsonify, request
from database import get_messages, get_all_users, get_user_by_api_key, save_message
from encryption import encrypt_message, decrypt_message
from config import API_PORT

app = Flask(__name__)

def check_api_key():
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None
    return get_user_by_api_key(api_key)

@app.route("/messages", methods=["GET"])
def messages():
    user = check_api_key()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    room = request.args.get("room", "general")
    rows = get_messages(room)
    result = []
    for sender, content, ts in rows:
        try:
            plain = decrypt_message(content)
        except:
            plain = "[encrypted]"
        result.append({"sender": sender, "content": plain, "timestamp": ts})
    return jsonify(result)

@app.route("/users", methods=["GET"])
def users():
    user = check_api_key()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(get_all_users())

@app.route("/send", methods=["POST"])
def send():
    user = check_api_key()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    if not data or "content" not in data or "room" not in data:
        return jsonify({"error": "Missing content or room"}), 400
    encrypted = encrypt_message(data["content"])
    save_message(user[1], data["room"], encrypted)
    return jsonify({"status": "sent"})

@app.route("/stats", methods=["GET"])
def stats():
    user = check_api_key()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    all_users = get_all_users()
    return jsonify({
        "total_users": len(all_users),
        "users": all_users
    })

def start_api():
    app.run(host="0.0.0.0", port=API_PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_api()