import telebot
import requests
import sqlite3
import threading
import time
import ast
from flask import Flask
from collections import Counter
import random

# Yangi token joylandi
TOKEN = '8626905693:AAFSVu2hJ3UIo4PzwGdxg3qPtkBQTGwSQO8'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# BAZANI SOZLASH
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

def fetch_real_numbers():
    try:
        url = "https://formula55.tj/api/v1/keno/history"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'draws' in data and len(data['draws']) > 0:
                save_to_db(data['draws'][0]['balls'])
    except: pass

# COMMAND HANDLERS
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot faol. Buyruqlar: /analiz, /stat, /tarix")

@bot.message_handler(commands=['analiz'])
def cmd_analiz(message):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    rows = conn.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 5000').fetchall()
    conn.close()
    if not rows: return
    all_nums = [num for row in rows for num in ast.literal_eval(row[0])]
    stats = Counter(all_nums).most_common(10)
    bot.reply_to(message, f"📊 Top 10 raqam: {[x[0] for x in stats]}")

@bot.message_handler(commands=['stat'])
def cmd_stat(message):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    count = conn.execute('SELECT COUNT(*) FROM results').fetchone()[0]
    conn.close()
    bot.reply_to(message, f"💾 Bazada {count} ta tiraj bor.")

@bot.message_handler(commands=['tarix'])
def cmd_tarix(message):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    rows = conn.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 5').fetchall()
    conn.close()
    bot.reply_to(message, f"📜 Oxirgi 5 ta tiraj:\n" + "\n".join([r[0] for r in rows]))

if __name__ == "__main__":
    init_db()
    # Web server
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    # API monitoring
    threading.Thread(target=lambda: [ (fetch_real_numbers(), time.sleep(300)) for _ in iter(int, 1)], daemon=True).start()
    
    # 409 Xatosini oldini olish uchun
    bot.remove_webhook()
    print("🤖 Bot ishga tushdi...")
    bot.infinity_polling(none_stop=True, skip_pending=True)
