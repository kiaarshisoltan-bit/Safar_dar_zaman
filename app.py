from flask import Flask, render_template, jsonify, request
import threading
import time
import requests
import random
import os

app = Flask(__name__)

# --- تنظیمات توکن ربات بله ---
TOKEN = os.environ.get("BOT_TOKEN", "توکن_ربات_بله_اینجا")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://safar-dar-zaman.onrender.com")
BALE_API = f"https://tapi.bale.ai/bot{TOKEN}"

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
        time.sleep(300)

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
        step_id = random.choice(POOL := FUTURE_POOL)
        
    current_node = STORY.get(step_id, STORY['start'])
    return jsonify(current_node)


# --- دریافت پیام‌ها از بله (Webhook) ---
@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return "OK", 200

    message = update.get('message') or update.get('callback_query', {}).get('message')
    if message:
        chat_id = message['chat']['id']
        text = message.get('text', '')

        if text == '/start':
            # ارسال پیام خوش‌آمدگویی به همراه دکمه شیشه‌ای وب‌اپ
            payload = {
                "chat_id": chat_id,
                "text": "سلام کیا جان! 🤖✨\nبه ماشین زمان خوش آمدید. برای ورود به دنیای گرافیکی و شروع ماجراجویی، روی دکمه زیر بزن:",
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "⏳ ورود به پورتال سفر در زمان",
                                "web_app": {"url": WEB_APP_URL}
                            }
                        ]
                    ]
                }
            }
            try:
                requests.post(f"{BALE_API}/sendMessage", json=payload, timeout=10)
            except Exception as e:
                print("خطا در ارسال پیام به بله:", e)

    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
