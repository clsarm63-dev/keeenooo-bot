import telebot
import requests
import sqlite3
import threading
import time
import ast
from flask import Flask
from collections import Counter
import random

TOKEN = '8626905693:AAFETRY88hXAY3g8ytn8AyKTnQCmdS89zIA'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, numbers TEXT)')
    conn.commit()
    conn.close()

def save_to_db(nums):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    # Ma'lumotni to'g'ridan-to'g'ri string sifatida yozamiz
    cursor.execute('INSERT INTO results (numbers) VALUES (?)', (str(nums),))
    conn.commit()
    conn.close()
    print(f"✅ Bazaga yozildi: {nums}") # LOG: terminalda ko'rinadi

def fetch_real_numbers():
    url = "https://formula55.tj/api/v1/keno/history"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # API javobini tekshiramiz
            if 'draws' in data and len(data['draws']) > 0:
                latest_draw = data['draws'][0]['balls'] 
                save_to_db(latest_draw)
            else:
                print("⚠️ API javobi bo'sh yoki format o'zgargan.")
        else:
            print(f"⚠️ API xatosi, status: {response.status_code}")
    except Exception as e:
        print(f"❌ API ulanish xatosi: {e}")

# ... qolgan handlerlar (analiz, stat, tarix) o'zgarishsiz ...

if __name__ == "__main__":
    init_db()
    
    # 1. API yig'ish jarayonini alohida thread'da ishga tushiramiz
    def monitor_loop():
        print("🔍 Monitoring ishga tushdi...")
        while True:
            fetch_real_numbers()
            time.sleep(300) # Har 5 daqiqada

    threading.Thread(target=monitor_loop, daemon=True).start()
    
    # 2. Web server
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    
    # 3. Bot
    print("🤖 Bot ishga tushdi...")
    bot.infinity_polling()
            
