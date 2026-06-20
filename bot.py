import telebot
import requests
import time
import threading
import os
from flask import Flask

# TOKEN va CHAT_ID ni o'zgartirmang (agar o'zgartirgan bo'lsangiz, o'zingiznikini qoldiring)
TOKEN = '8626905693:AAEwBArwg1q2kMyG6GwTsKJVNUehVkGgS8I'
CHAT_ID = '5946640227'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# YANGILANGAN fetch_data funksiyasi
def fetch_data():
    try:
        url = "https://formula55.tj/"
        # Saytning botlardan himoyasini chetlab o'tish uchun kuchaytirilgan headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return "Sayt ishlamoqda: OK"
        else:
            return f"Sayt xato javob berdi: {response.status_code}"
            
    except Exception as e:
        return f"Ulanish xatosi: {e}"

def run_bot():
    bot.remove_webhook()
    while True:
        try:
            status = fetch_data()
            bot.send_message(CHAT_ID, f"Bot holati: {status}")
        except Exception as e:
            print(f"Xatolik: {e}")
        time.sleep(3600) # Har 1 soatda yangilaydi

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    run_bot()
