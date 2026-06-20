import telebot
import sqlite3
import threading
import time
import ast
import cloudscraper
from flask import Flask, request
from collections import Counter

TOKEN = '8626905693:AAFSVu2hJ3UIo4PzwGdxg3qPtkBQTGwSQO8'
# Webhook uchun URL (Render'dagi o'z URL manzilingizni yozing)
WEBHOOK_URL = "https://sening-proyekt-noming.onrender.com/"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# BAZA VA API
def init_db():
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, numbers TEXT)')
    conn.commit()
    conn.close()

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

# WEBHOOK ENDPOINT
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

# BOT BUYRUQLARI
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot Webhook rejimida ishlamoqda!")

# ... Qolgan analiz, stat, tarix handlerlarini shu yerga qo'shing ...

if __name__ == "__main__":
    init_db()
    # Webhook'ni o'rnatish
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + TOKEN)
    
    # API monitoring
    threading.Thread(target=lambda: [ (fetch_real_numbers(), time.sleep(300)) for _ in iter(int, 1)], daemon=True).start()
    
    # Serverni ishga tushirish
    app.run(host='0.0.0.0', port=8080)
    
