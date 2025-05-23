from flask import Flask, request
import requests
import logging
import os
import threading
import time
from db_helper import init_db, get_top_discounts  # فرض می‌گیریم این ماژول تو دیتابیس رو مدیریت می‌کنه

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # متغیر محیطی باید ست شده باشه
if not BOT_TOKEN:
    logging.error("Error: BOT_TOKEN environment variable is not set!")
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

user_chat_ids = set()

def send_message(chat_id, text):
    url = f'{TELEGRAM_API_URL}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    try:
        resp = requests.post(url, json=payload)
        if resp.status_code != 200:
            logging.error(f"Failed to send message to {chat_id}: {resp.text}")
    except Exception as e:
        logging.error(f"Exception while sending message to {chat_id}: {e}")

def discount_job():
    while True:
        logging.info("Checking discounts...")
        discounts = get_top_discounts()

        if discounts:
            message = "🔥 تخفیف‌های بالای ۳۰٪:\n\n"
            for name, discount, link in discounts:
                message += f"{name} - {discount}%\n{link}\n\n"
            for chat_id in user_chat_ids:
                send_message(chat_id, message)
        else:
            logging.info("No discounts found.")
        time.sleep(180)  # هر ۳ دقیقه

@app.route('/', methods=['GET'])
def home():
    return 'Bot is running!', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    logging.info(f"Received update: {update}")

    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        if text == '/start':
            user_chat_ids.add(chat_id)
            send_message(chat_id, 'سلام! شما به دریافت‌کنندگان تخفیف‌های ویژه اضافه شدید.')
        else:
            send_message(chat_id, f'پیام شما دریافت شد: {text}')

    return 'ok', 200

if __name__ == '__main__':
    init_db()  # مقداردهی دیتابیس (فقط یک بار)
    threading.Thread(target=discount_job, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
