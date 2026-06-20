import telebot
import requests
import sqlite3
import threading
import time
import ast
from flask import Flask
from collections import Counter
import random

TOKEN = '8626905693:AAEwBArwg1q2kMyG6GwTsKJVNUehVkGgS8I'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# BAZANI SOZLASH
def init_db():
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tirajlar cheksiz yig'iladi, takrorlansa ham yoziladi
    cursor.execute('CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, numbers TEXT)')
    conn.commit()
    conn.close()

def save_to_db(nums):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO results (numbers) VALUES (?)', (str(nums),))
    conn.commit()
    conn.close()

def fetch_real_numbers():
    try:
        url = "https://formula55.tj/api/v1/keno/history"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            latest_draw = data['draws'][0]['balls'] 
            save_to_db(latest_draw)
    except Exception as e:
        print(f"API xatosi: {e}")

# ANALIZ: 5000 TIRAJ BO'YICHA
@bot.message_handler(commands=['analiz'])
def cmd_analiz(message):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    # Bazadan eng oxirgi 5000 ta tirajni olish
    cursor.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 5000')
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) < 10: 
        bot.reply_to(message, f"⚠️ Ma'lumot kam. Hozir bazada {len(rows)} ta tiraj bor.")
        return

    all_nums = [num for row in rows for num in ast.literal_eval(row[0])]
    stats = Counter(all_nums)
    
    top_3 = [x[0] for x in stats.most_common(3)]
    most_common_10 = [x[0] for x in stats.most_common(10)]
    prognoz = random.sample(most_common_10, 3) 
    
    bot.reply_to(message, f"📊 **{len(rows)} tiraj tahlili:**\n\n"
                          f"🏆 Top 3 (Eng ko'p chiqqan): {top_3}\n"
                          f"🎯 Prognoz (Ehtimoliy): {prognoz}", parse_mode="Markdown")

@bot.message_handler(commands=['stat'])
def cmd_stat(message):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM results')
    count = cursor.fetchone()[0]
    conn.close()
    bot.reply_to(message, f"💾 Bazada jami yig'ilgan tirajlar soni: {count}")

@bot.message_handler(commands=['tarix'])
def cmd_tarix(message):
    conn = sqlite3.connect('game_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    text = "\n".join([f"Tiraj: {r[0]}" for r in rows])
    bot.reply_to(message, f"📜 Oxirgi 5 ta tiraj:\n{text}")

if __name__ == "__main__":
    init_db()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    
    while True:
        fetch_real_numbers()
        time.sleep(300) 
    
