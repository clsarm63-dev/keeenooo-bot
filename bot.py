import telebot
import sqlite3
import threading
import time
import cloudscraper
from flask import Flask

TOKEN = '8626905693:AAFSVu2hJ3UIo4PzwGdxg3qPtkBQTGwSQO8'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# BAZA
def init_db():
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, numbers TEXT)')
    conn.commit()
    conn.close()

# API
def fetch_real_numbers():
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get("https://formula55.tj/api/v1/keno/history", timeout=20)
        if response.status_code == 200:
            data = response.json()
            if 'draws' in data:
                nums = str(data['draws'][0]['balls'])
                conn = sqlite3.connect('game_data.db', check_same_thread=False)
                conn.execute('INSERT INTO results (numbers) VALUES (?)', (nums,))
                conn.commit()
                conn.close()
    except Exception as e:
        print(f"API Xatosi: {e}")

@app.route('/')
def home():
    return "Bot ishlamoqda!"

# BOT BUYRUQLARI
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot ishlamoqda!")

if __name__ == "__main__":
    init_db()
    # API monitoring
    threading.Thread(target=lambda: [ (fetch_real_numbers(), time.sleep(300)) for _ in iter(int, 1)], daemon=True).start()
    
    # Web server
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    
    # 409 xatosini yengish uchun eng muhim qism:
    bot.remove_webhook()
    print("Bot polling boshladi...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
