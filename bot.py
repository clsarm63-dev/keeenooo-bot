import telebot
import requests
import time
import threading
from bs4 import BeautifulSoup

TOKEN = "8626905693:AAG1Ecjk-W95hBlgDKo1B844YpUHUxG9ru8" 
bot = telebot.TeleBot(TOKEN)
CHAT_ID = '5946640227'

# Saytdan ma'lumot olish funksiyasi
def fetch_formula55_data():
    try:
        url = "https://formula55.tj/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Bu yerda saytning o'zgarishini kuzatish uchun logikani qo'shamiz
            # Masalan, top o'yinlar sarlavhasini olish
            return "Ma'lumotlar yangilandi: Formula55 sayti faol."
        return "Saytga ulanishda muammo bor."
    except Exception as e:
        return f"Xatolik: {e}"

# Botning doimiy xabar yuborish funksiyasi (Background Task)
def background_task():
    while True:
        data = fetch_formula55_data()
        bot.send_message(CHAT_ID, f"Monitoring holati: {data}")
        # Har 1 soatda (3600 soniya) tekshiradi
        time.sleep(3600)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot ishga tushdi! Men har soatda ma'lumotlarni tekshirib turaman.")

# Asosiy qism
if __name__ == "__main__":
    # Fon jarayonini ishga tushirish
    threading.Thread(target=background_task, daemon=True).start()
    # Botni ishga tushirish
    bot.infinity_polling()
  
