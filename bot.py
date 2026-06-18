import telebot
import requests
import time
import threading
from bs4 import BeautifulSoup

# TOKEN va ID ni o'zingizniki bilan almashtiring
TOKEN = '8626905693:AAG1Ecjk-W95hBlgDKo1B844YpUH...'
CHAT_ID = '5946640227'

bot = telebot.TeleBot(TOKEN)

def fetch_data():
    try:
        url = "https://formula55.tj/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return "Sayt ishlamoqda: OK"
        return f"Sayt xatolik berdi: {response.status_code}"
    except Exception as e:
        return f"Ulanish xatosi: {e}"

def run_bot():
    # Eski webhook larni tozalash - 409 xatosini yo'qotadi
    bot.remove_webhook()
    print("Bot ishga tushdi...")
    bot.infinity_polling(none_stop=True, interval=0)

if __name__ == "__main__":
    # Botni alohida oqimda ishga tushiramiz
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Doimiy xabar yuborish sikli
    while True:
        try:
            status = fetch_data()
            bot.send_message(CHAT_ID, f"Bot holati: {status}")
        except Exception as e:
            print(f"Xabar yuborishda xato: {e}")
        
        # Har 1 soatda (3600 soniya) yangilaydi
        time.sleep(3600)
