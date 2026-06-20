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
# MUHIM: Telegramdagi eski ulanishlarni o'chirib tashlaydi
bot.remove_webhook() 
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
    cursor.execute('INSERT INTO results (numbers) VALUES (?)', (str(nums),))
    conn.commit()
    conn.close()
    print(f"✅ Tiraj saqlandi: {nums}")

def fetch_real_numbers():
    url = "https://formula55.tj/api/v1/keno/history"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'draws' in data and len(data['draws']) > 0:
                latest_draw = data['draws'][0]['balls']
                save_to_db(latest_draw)
    except Exception as e:
        print(f"❌ API xatosi: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men Keno tahlil botiman.\n/analiz - Statistik Top 10 va Prognoz\n/top3 - Eng ko'p chiqqan 3 lik\n/stat - Bazadagi jami tirajlar\n/tarix - Oxirgi 5 ta tiraj")

@bot.message_handler(commands=['analiz'])
def cmd_analiz(message):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 5000')
    rows = cursor.fetchall()
    conn.close()
    if len(rows) < 10: 
        bot.reply_to(message, "⚠️ Ma'lumot to'planmoqda, biroz kuting.")
        return
    all_nums = [num for row in rows for num in ast.literal_eval(row[0])]
    stats = Counter(all_nums)
    top_3 = [x[0] for x in stats.most_common(3)]
    most_common_10 = [x[0] for x in stats.most_common(10)]
    prognoz = random.sample(most_common_10, 3) 
    bot.reply_to(message, f"📊 **Statistika ({len(rows)} tiraj):**\n🏆 Top 3: {top_3}\n🎯 Prognoz: {prognoz}", parse_mode="Markdown")

@bot.message_handler(commands=['stat'])
def cmd_stat(message):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM results')
    count = cursor.fetchone()[0]
    conn.close()
    bot.reply_to(message, f"💾 Bazada {count} ta tiraj bor.")

@bot.message_handler(commands=['tarix'])
def cmd_tarix(message):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    text = "\n".join([f"Tiraj: {r[0]}" for r in rows])
    bot.reply_to(message, f"📜 Oxirgi 5 ta:\n{text}")

if __name__ == "__main__":
    init_db()
    # Web server
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    # API monitoring
    threading.Thread(target=lambda: [ (fetch_real_numbers(), time.sleep(300)) for _ in iter(int, 1)], daemon=True).start()
    
    print("🤖 Bot ishga tushmoqda...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
    
