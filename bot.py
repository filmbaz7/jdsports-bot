from flask import Flask, request
import requests
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')  # توکن ربات رو از متغیر محیطی بخون

TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

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

        send_message(chat_id, f'پیام شما دریافت شد: {text}')

    return 'ok', 200

def send_message(chat_id, text):
    url = f'{TELEGRAM_API_URL}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
