import telebot
import requests
import time
import threading
import os
from flask import Flask
from bs4 import BeautifulSoup

# TOKEN va CHAT_ID ni o'zgartiring
TOKEN = '8626905693:AAEwBArwg1q2kMyG6GwTsKJVNUehVkGgS8I'
CHAT_ID = '5946640227'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Render portini ochish uchun
@app.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Saytdan ma'lumot olish funksiyasi
def fetch_data():
    try:
        url = "https://formula55.tj/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        return "Sayt ishlamoqda" if response.status_code == 200 else f"Xato: {response.status_code}"
    except Exception as e:
        return f"Ulanish xatosi: {e}"

# Botni ishga tushirish funksiyasi
def run_bot():
    bot.remove_webhook()
    while True:
        try:
            status = fetch_data()
            bot.send_message(CHAT_ID, f"Bot holati: {status}")
        except Exception as e:
            print(f"Xatolik: {e}")
        time.sleep(3600) # Har soatda xabar yuboradi

if __name__ == "__main__":
    # Veb serverni alohida oqimda (thread) ishga tushirish
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    # Botni asosiy oqimda ishga tushirish
    run_bot()
  
