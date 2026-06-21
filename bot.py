import telebot
import sqlite3
import threading
import time
import ast
import cloudscraper
import random
from flask import Flask
from collections import Counter

# --- SOZLAMALAR ---
TOKEN = '8626905693:AAFMaVXp45-5nfPTfHe2pP-tu4BVXjfD9ok'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- BAZA BILAN ISHLASH ---
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

# --- API DAN MA'LUMOT OLISH ---
def fetch_real_numbers():
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get("https://formula55.tj/api/v1/keno/history", timeout=20)
        if response.status_code == 200:
            data = response.json()
            if 'draws' in data and data['draws']:
                nums = data['draws'][0]['balls'] # List ko'rinishida
                save_to_db(nums)
    except Exception as e:
        print(f"API Xatosi: {e}")

# --- WEB SERVER (RENDER UCHUN) ---
@app.route('/')
def home():
    return "Bot faol!"

# --- BOT KOMANDALARI ---
@bot.message_handler(commands=['start', 'analiz', 'stat', 'tarix'])
def handle_commands(message):
    cmd = message.text
    
    if cmd == '/start':
        bot.reply_to(message, "Bot ishga tushdi! Buyruqlar:\n/analiz - Chuqur tahlil va prognoz\n/stat - Baza holati\n/tarix - Oxirgi natijalar")
    
    elif cmd == '/stat':
        conn = sqlite3.connect('game_data.db', check_same_thread=False)
        count = conn.execute('SELECT COUNT(*) FROM results').fetchone()[0]
        conn.close()
        bot.reply_to(message, f"💾 Bazada {count} ta tiraj saqlangan.")
        
    elif cmd == '/tarix':
        conn = sqlite3.connect('game_data.db', check_same_thread=False)
        rows = conn.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 5').fetchall()
        conn.close()
        text = "\n".join([r[0] for r in rows]) if rows else "Baza bo'sh."
        bot.reply_to(message, f"📜 Oxirgi 5 ta tiraj:\n{text}")
            
    elif cmd == '/analiz':
        conn = sqlite3.connect('game_data.db', check_same_thread=False)
        # 5000 ta tirajni olish
        rows = conn.execute('SELECT numbers FROM results ORDER BY id DESC LIMIT 5000').fetchall()
        conn.close()
        
        if not rows:
            bot.reply_to(message, "⚠️ Hali ma'lumot yetarli emas (5000 ta tiraj yig'ilmagan).")
            return
            
        all_nums = [num for row in rows for num in ast.literal_eval(row[0])]
        counts = Counter(all_nums)
        
        top_10 = counts.most_common(10) # Eng ko'p chiqqanlar
        bottom_10 = counts.most_common()[:-11:-1] # Eng kam chiqqanlar
        
        top_nums = [x[0] for x in top_10]
        prognoz = random.sample(top_nums, 3)
        
        msg = (
            f"📊 **5000 ta tiraj tahlili:**\n\n"
            f"🔥 **Eng ko'p chiqqan 10 ta:** {top_nums}\n"
            f"❄️ **Eng kam chiqqan 10 ta:** {[x[0] for x in bottom_10]}\n\n"
            f"🎯 **Prognoz (uchlik):** {prognoz}"
        )
        bot.reply_to(message, msg, parse_mode="Markdown")

# --- ASOSIY QISM ---
if __name__ == "__main__":
    init_db()
    # 5 daqiqada bir ma'lumot yangilash
    threading.Thread(target=lambda: [ (fetch_real_numbers(), time.sleep(300)) for _ in iter(int, 1)], daemon=True).start()
    # Web server
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    
    bot.remove_webhook()
    print("🤖 Bot ishga tushdi...")
    bot.infinity_polling(skip_pending=True)
