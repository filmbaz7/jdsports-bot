import os
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8443))

updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher
bot = updater.bot

USERS_FILE = "users.txt"

def save_user(chat_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, 'w').close()
    with open(USERS_FILE, "r") as f:
        ids = f.read().splitlines()
    if str(chat_id) not in ids:
        with open(USERS_FILE, "a") as f:
            f.write(str(chat_id) + "\n")

def send_to_all(text):
    if not os.path.exists(USERS_FILE):
        return
    with open(USERS_FILE, "r") as f:
        ids = f.read().splitlines()
    for user_id in ids:
        try:
            bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            print(f"❌ خطا در ارسال به {user_id}: {e}")

def start(update, context):
    chat_id = update.message.chat_id
    save_user(chat_id)
    update.message.reply_text("👋 سلام! به محض اینکه تخفیف خوبی پیدا کنیم، بهت پیام می‌دیم.")

import subprocess
import json

def fetch_discounts():
    subprocess.run(["python", "scraper_runner.py"])
    if not os.path.exists("output.json"):
        return
    with open("output.json", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        return

    for item in data:
        text = f"""🛍️ {item['name']}
💸 قبل: €{item['priceWas']}  👉 حالا: €{item['priceIs']}
📉 تخفیف: {item['discount']}٪
🔗 لینک محصول: {item['link']}"""
        send_to_all(text)

def main():
    dispatcher.add_handler(CommandHandler("start", start))

    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_discounts, 'interval', minutes=30)
    scheduler.start()

    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN
    )
    updater.bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    updater.idle()

if __name__ == "__main__":
    main()
