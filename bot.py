import telebot
import requests
import time
import threading
from bs4 import BeautifulSoup

TOKEN = '8626905693:AAG1Ecjk-W95hBlgDKo1B844YpUH...'
bot = telebot.TeleBot(TOKEN)
CHAT_ID = '5946640227'

def fetch_formula55_data():
    try:
        url = "https://formula55.tj/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return "Sayt ishlamoqda."
        return "Saytda muammo bor."
    except Exception as e:
        return f"Xatolik: {e}"

def background_task():
    while True:
        data = fetch_formula55_data()
        bot.send_message(CHAT_ID, f"Holat: {data}")
        time.sleep(3600)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot ishga tushdi!")

if __name__ == "__main__":
    threading.Thread(target=background_task, daemon=True).start()
    bot.infinity_polling()
