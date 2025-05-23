from flask import Flask, request
import requests
import logging
import os
import threading
import time
from bs4 import BeautifulSoup
import sqlite3

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

DB_PATH = 'users.db'

def check_write_permission(path='.'):
    test_file = os.path.join(path, 'test_write.txt')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logging.info("دسترسی نوشتن روی پوشه وجود دارد ✅")
        return True
    except Exception as e:
        logging.error(f"دسترسی نوشتن روی پوشه وجود ندارد ❌: {e}")
        return False

def init_db():
    if not check_write_permission():
        logging.error("دسترسی نوشتن وجود ندارد. دیتابیس ساخته نمی‌شود.")
        return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("دیتابیس و جدول‌ها ساخته شدند.")
    return True

def add_user(chat_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (chat_id) VALUES (?)', (chat_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        # chat_id قبلا بود، کاری نمی‌کنیم
        pass
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM users')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def send_message(chat_id, text):
    url = f'{TELEGRAM_API_URL}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, json=payload)

def fetch_discounts():
    url = "https://www.jdsports.com/en-eu/sale/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    discounts = []

    for item in soup.select('.product-tile'):
        title = item.select_one('.product-title').get_text(strip=True)
        try:
            discount_text = item.select_one('.discount').get_text(strip=True)
            discount_value = int(discount_text.replace('%', '').replace('-', ''))
        except:
            discount_value = 0

        if discount_value >= 30:
            link = item.select_one('a')['href']
            full_link = "https://www.jdsports.com" + link
            discounts.append(f"{title} - تخفیف {discount_value}%\n{full_link}")

    return discounts

def discount_job():
    while True:
        logging.info("Fetching discounts...")
        discounts = fetch_discounts()
        if discounts:
            message = "🔥 تخفیف‌های بالای ۳۰٪ JD Sports:\n\n" + "\n\n".join(discounts)
            users = get_all_users()
            for chat_id in users:
                send_message(chat_id, message)
        else:
            logging.info("No discounts found.")
        time.sleep(180)

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
            add_user(chat_id)
            send_message(chat_id, 'سلام! شما به لیست تخفیف‌ها اضافه شدید.')
        else:
            send_message(chat_id, f'پیام شما دریافت شد: {text}')

    return 'ok', 200

if __name__ == '__main__':
    if init_db():
        port = int(os.environ.get('PORT', 5000))
        threading.Thread(target=discount_job, daemon=True).start()
        app.run(host='0.0.0.0', port=port)
    else:
        logging.error("ربات به دلیل نداشتن دسترسی نوشتن اجرا نمی‌شود.")
