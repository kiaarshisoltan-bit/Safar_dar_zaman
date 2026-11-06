from flask import Flask, render_template, jsonify, request
import threading
import time
import requests
import random
import os
from telebot import TeleBot, types

app = Flask(__name__)

# --- تنظیمات توکن ربات بله ---
TOKEN = os.environ.get("BOT_TOKEN", "توکن_ربات_بله_اینجا")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://safar-dar-zaman.onrender.com")

# ساخت نمونه ربات و تنظیم آدرس اختصاصی سرور پیام‌رسان بله
bot = TeleBot(TOKEN)
bot.api_url = "https://tapi.bale.ai/bot{0}/{1}"

# --- سیستم پینگ داخلی برای جلوگیری از خواب سرور ---
def keep_alive():
    url = os.environ.get("SELF_URL", f"{WEB_APP_URL}/health")
    time.sleep(10)
    while True:
        try:
            response = requests.get(url, timeout=10)
            print("✅ پینگ خودکار موفق:", response.status_code)
        except Exception as e:
            print("❌ خطا در پینگ خودکار:", e)
        time.sleep(300)  # هر ۵ دقیقه

threading.Thread(target=keep_alive, daemon=True).start()

@app.route('/health')
def health():
    return "OK", 200

# --- دیتابیس داستان‌ها و چالش‌های رندوم ---
STORY = {
    "start": {
        "theme": "present",
        "title": "آزمایشگاه زمان (حال)",
        "text": "تو وسط یک آزمایشگاه تاریک ایستادی. روبه‌روت ماشین زمان روشن است. به کدامین عصر سفر می‌کنی؟",
        "choices": [
            {"text": "سفر به گذشته (تاریخ ناشناخته)", "next": "random_past"},
            {"text": "سفر به آینده (دنیای مرموز)", "next": "random_future"}
        ]
    },
    "middle_ages_1": {
        "theme": "past",
        "title": "قرون وسطی - قلعه محاصره شده",
        "text": "هوای مهیب و بوی باروت! شوالیه‌ها دارن به قلعه حمله می‌کنن و تو رو به عنوان جاسوس دستگیر کردن!",
        "choices": [
            {"text": "تلاش برای فرار با اسب پادشاه", "next": "past_escape_success"},
            {"text": "اثبات بی‌گناهی با ترفند ساختگی", "next": "past_magic_fail"},
            {"text": "بازگشت به آزمایشگاه (حال)", "next": "start"}
        ]
    },
    "future_city_1": {
        "theme": "future",
        "title": "شهر نئونی (سال ۳۰۲۰)",
        "text": "آسمان‌خراش‌های معلق و ربات‌های گشت‌زنی. پلیس رباتیک بهت دستور توقف میده!",
        "choices": [
            {"text": "هک کردن پهپاد پلیس با مچ‌بند هوشمند", "next": "future_hack_success"},
            {"text": "پرش از پشت‌بام روی ماشین پرنده عبوری", "next": "future_fly_danger"},
            {"text": "بازگشت به آزمایشگاه (حال)", "next": "start"}
        ]
    },
    "past_escape_success": {
        "theme": "past",
        "title": "فرار بزرگ",
        "text": "با مهارت تمام از دست شوالیه‌ها دررفتی و گنجینه‌ای از طلا هم با خودت آوردی!",
        "choices": [{"text": "شروع دوباره ماجراجویی", "next": "start"}]
    },
    "future_hack_success": {
        "theme": "future",
        "title": "هکر ارشد آینده",
        "text": "سیستم امنیتی شهر رو دور زدی و حالا تمام ربات‌ها به فرمان تو هستن!",
        "choices": [{"text": "شروع دوباره ماجراجویی", "next": "start"}]
    }
}

PAST_POOL = ["middle_ages_1"]
FUTURE_POOL = ["future_city_1"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/step', methods=['POST'])
def step():
    data = request.get_json()
    step_id = data.get('step', 'start')
    
    if step_id == 'random_past':
        step_id = random.choice(PAST_POOL)
    elif step_id == 'random_future':
        step_id = random.choice(FUTURE_POOL)
        
    current_node = STORY.get(step_id, STORY['start'])
    return jsonify(current_node)


# --- هندلر دستور استارت ربات بله ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    web_app = types.WebAppInfo(url=WEB_APP_URL)
    btn = types.InlineKeyboardButton(text="⏳ ورود به پورتال سفر در زمان", web_app=web_app)
    markup.add(btn)
    
    bot.send_message(
        message.chat.id, 
        "سلام کیا جان! 🤖✨\nبه ماشین زمان خوش آمدید. برای ورود به دنیای گرافیکی و شروع ماجراجویی، روی دکمه زیر بزن:", 
        reply_markup=markup
    )


# اجرای ربات به صورت پولینگ در یک ترد جداگانه
def run_bot():
    print("🤖 ربات بله روشن شد...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print("خطا در ربات:", e)
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
