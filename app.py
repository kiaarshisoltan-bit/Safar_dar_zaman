from flask import Flask, render_template, jsonify, request
import threading
import time
import requests
import os

app = Flask(__name__)

# --- سیستم پینگ داخلی برای جلوگیری از خواب زودهنگام ---
def keep_alive():
    # لینک سایتت رو از متغیر محیطی می‌خونه، اگه نبود پیش‌فرض همینه
    url = os.environ.get("SELF_URL", "https://safar-dar-zaman.onrender.com/health")
    time.sleep(10)  # چند ثانیه صبر می‌کنه تا سرور کاملاً بالا بیاد
    while True:
        try:
            response = requests.get(url, timeout=10)
            print("✅ پینگ خودکار موفق:", response.status_code)
        except Exception as e:
            print("❌ خطا در پینگ خودکار:", e)
        time.sleep(300)  # هر ۵ دقیقه (۳۰۰ ثانیه) یک بار

# اجرای ترد (Thread) در پس‌زمینه
threading.Thread(target=keep_alive, daemon=True).start()

@app.route('/health')
def health():
    return "OK", 200

# دیتابیس داستان سفر در زمان
STORY = {
    "start": {
        "theme": "present",
        "title": "آزمایشگاه زمان (حال)",
        "text": "تو وسط یک آزمایشگاه تاریک ایستادی. روبه‌روت ماشین زمان روشن است. کدام دکمه را می‌فشاری؟",
        "choices": [
            {"text": "سفر به گذشته (قرن وسطی)", "next": "middle_ages"},
            {"text": "سفر به آینده (سال ۳۰۲۰)", "next": "future_city"}
        ]
    },
    "middle_ages": {
        "theme": "past",
        "title": "قرون وسطی - قلعه تاریک",
        "text": "هوای مهیب و بوی باروت! شوالیه‌ها دارن به قلعه حمله می‌کنن. نگهبان‌ها بهت مشکوک شدن!",
        "choices": [
            {"text": "فرار به جنگل مه‌آلود", "next": "dark_forest"},
            {"text": "بازگشت به آزمایشگاه (حال)", "next": "start"}
        ]
    },
    "future_city": {
        "theme": "future",
        "title": "شهر نئونی (سال ۳۰۲۰)",
        "text": "آسمان‌خراش‌های معلق، ماشین‌های پرنده و ربات‌های نگهبان! همه‌چیز دیجیتالی و رنگارنگه.",
        "choices": [
            {"text": "هک کردن سیستم مرکزی شهر", "next": "hacked_system"},
            {"text": "بازگشت به آزمایشگاه (حال)", "next": "start"}
        ]
    },
    "dark_forest": {
        "theme": "past",
        "title": "جنگل مه‌آلود",
        "text": "تو توی مه گم شدی و صدای گرگ‌ها میاد... ناگهان یک پورتال جادویی پیدا می‌کنی!",
        "choices": [
            {"text": "ورود به پورتال ناشناخته", "next": "future_city"},
            {"text": "بازگشت به آزمایشگاه (حال)", "next": "start"}
        ]
    },
    "hacked_system": {
        "theme": "future",
        "title": "پایان پیروزمندانه!",
        "text": "آفرین! تو سیستم آینده رو هک کردی و راز سفر در زمان رو کشف کردی. تو ارباب زمانی!",
        "choices": [
            {"text": "شروع دوباره ماجراجویی", "next": "start"}
        ]
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/step', methods=['POST'])
def step():
    data = request.get_json()
    step_id = data.get('step', 'start')
    current_node = STORY.get(step_id, STORY['start'])
    return jsonify(current_node)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
