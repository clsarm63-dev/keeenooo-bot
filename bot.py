import telebot
import sqlite3
import threading
import time
import ast
import cloudscraper  # Cloudflare himoyasini yengish uchun
from flask import Flask
from collections import Counter

TOKEN = '8626905693:AAFSVu2hJ3UIo4PzwGdxg3qPtkBQTGwSQO8'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, numbers TEXT)')
    conn.commit()
    conn.close()

def save_to_db(nums):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    conn.execute('INSERT INTO results (numbers) VALUES (?)', (str(nums),))
    conn.commit()
    conn.close()
    print(f"✅ Bazaga yozildi: {nums}")

def fetch_real_numbers():
    scraper = cloudscraper.create_scraper() # Himoyani chetlab o'tuvchi obyekt
    url = "https://formula55.tj/api/v1/keno/history"
    try:
        response = scraper.get(url, timeout=20)
        print(f"DEBUG: Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'draws' in data and len(data['draws']) > 0:
                save_to_db(data['draws'][0]['balls'])
            else:
                print("⚠️ API javobi kutilganidek emas.")
        else:
            print(f"❌ Server rad etdi: {response.status_code}")
    except Exception as e:
        print(f"❌ Xatolik: {e}")

def monitor_loop():
    while True:
        fetch_real_numbers()
        time.sleep(300) # 5 daqiqa

# Bot buyruqlari...
@bot.message_handler(commands=['start', 'analiz', 'stat', 'tarix'])
def handle_commands(message):
    if message.text == '/start':
        bot.reply_to(message, "Bot faol va ma'lumot yig'moqda.")
    elif message.text == '/stat':
        conn = sqlite3.connect('game_data.db', check_same_thread=False)
        count = conn.execute('SELECT COUNT(*) FROM results').fetchone()[0]
        conn.close()
        bot.reply_to(message, f"💾 Bazada {count} ta tiraj bor.")
    # ... qolganlari ...

if __name__ == "__main__":
    init_db()
    threading.Thread(target=monitor_loop, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    
    bot.remove_webhook()
    bot.infinity_polling()
    
