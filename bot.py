
import telebot
import requests
import sqlite3
import threading
import time
import random
from flask import Flask
from collections import Counter

# Siz bergan yangi token
TOKEN = '8626905693:AAEwBArwg1q2kMyG6GwTsKJVNUehVkGgS8I'
CHAT_ID = '5946640227'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# BAZANI TAYYORLASH
def init_db():
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, numbers TEXT)')
    conn.commit()
    conn.close()

# MA'LUMOT SAQLASH
def save_to_db(nums):
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO results (numbers) VALUES (?)', (str(nums),))
    conn.commit()
    conn.close()

# ANALIZ VA PROGNOZ
def analyze():
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 50')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows: return "⚠️ Hali ma'lumot yetarli emas."
    
    all_nums = [int(n) for row in rows for n in eval(row[0])]
    counter = Counter(all_nums)
    
    top_3 = [x[0] for x in counter.most_common(3)]
    top_10 = [x[0] for x in counter.most_common(10)]
    
    return (f"📊 *Oxirgi 50 tiraj tahlili:*\n\n"
            f"🏆 Top 3 raqam: {top_3}\n"
            f"🔮 Top 10 ehtimoliy: {top_10}\n\n"
            f"🎯 *Prognoz:* {random.sample(top_10, 3)}")

# BOT BUYRUQLARI
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men Keno tahlil botiman. /analiz yoki /tarix buyruqlaridan foydalaning.")

@bot.message_handler(commands=['analiz'])
def send_analiz(message):
    bot.reply_to(message, analyze(), parse_mode="Markdown")

@bot.message_handler(commands=['tarix'])
def send_history(message):
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    text = "\n".join([f"Tiraj: {r[0]}" for r in rows])
    bot.reply_to(message, f"📜 Oxirgi 5 ta tiraj:\n{text}")

# ISHGA TUSHIRISH
if __name__ == "__main__":
    init_db()
    # Web server
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    # Bot polling
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    print("Bot muvaffaqiyatli ishga tushdi!")
    while True:
        time.sleep(3600)
