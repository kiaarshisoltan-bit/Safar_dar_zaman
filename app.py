from flask import Flask, render_template, jsonify, request
import threading
import time
import requests
import random
import os

app = Flask(__name__)

# --- سیستم پینگ داخلی برای جلوگیری از خواب زودهنگام ---
def keep_alive():
    url = os.environ.get("SELF_URL", "https://safar-dar-zaman.onrender.com/health")
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

# --- دیتابیس داستان‌ها و چالش‌های متنوع (رندوم) ---
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
    
    # سناریوهای گذشته (شماره ۱: قلعه محاصره شده)
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
    
    # سناریوهای گذشته (شماره ۲: مصر باستان)
    "middle_ages_2": {
        "theme": "past",
        "title": "مصر باستان - هرم اسرارآمیز",
        "text": "توی یک مقبره تاریک و پر از تله‌های باستانی گیر افتادی. مشعلت داره خاموش میشه!",
        "choices": [
            {"text": "حل معما و باز کردن صندوقچه فرعونی", "next": "past_pharaoh_win"},
            {"text": "دویدن کورکورانه در راهروهای تاریک", "next": "past_trap_fail"},
            {"text": "بازگشت به آزمایشگاه (حال)", "next": "start"}
        ]
    },

    # سناریوهای آینده (شماره ۱: شهر نئونی)
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

    # سناریوهای آینده (شماره ۲: مریخ سرخ)
    "future_city_2": {
        "theme": "future",
        "title": "کلونی مریخ (سال ۲۱۵۰)",
        "text": "اکسیژن گنبد داره تموم میشه و آلارم هشدار قرمز همه‌جا رو پر کرده!",
        "choices": [
            {"text": "تعمیر مخزن اکسیژن اصلی با ابزار اضطراری", "next": "future_mars_win"},
            {"text": "فرار به سمت سفینه نجات اضطراری", "next": "future_escape_pod"},
            {"text": "بازگشت به آزمایشگاه (حال)", "next": "start"}
        ]
    },

    # پایان‌های مثبت و منفی گذشته
    "past_escape_success": {
        "theme": "past",
        "title": "فرار بزرگ از قرون وسطی",
        "text": "با مهارت تمام از دست شوالیه‌ها دررفتی و گنجینه‌ای از طلا هم با خودت آوردی! قهرمان تاریخ شدی.",
        "choices": [{"text": "شروع دوباره ماجراجویی", "next": "start"}]
    },
    "past_magic_fail": {
        "theme": "past",
        "title": "سیاه‌چال تاریک",
        "text": "شوالیه‌ها فریب ترفندتو نخوردن و انداختنت توی سیاه‌چال! بازی تموم شد.",
        "choices": [{"text": "تلاش مجدد در زمان", "next": "start"}]
    },
    "past_pharaoh_win": {
        "theme": "past",
        "title": "گنجینه فرعون",
        "text": "معمای هرم رو به درستی حل کردی و راز جاودانگی رو کشف کردی! فوق‌العاده بودی.",
        "choices": [{"text": "شروع دوباره ماجراجویی", "next": "start"}]
    },
    "past_trap_fail": {
        "theme": "past",
        "title": "تله‌های باستانی",
        "text": "توی تاریکی پات رفت رو سنگ فشار و تیرهای زهرآگین به سمتت پرتاب شدن...",
        "choices": [{"text": "تلاش مجدد در زمان", "next": "start"}]
    },

    # پایان‌های مثبت و منفی آینده
    "future_hack_success": {
        "theme": "future",
        "title": "هکر ارشد آینده",
        "text": "سیستم امنیتی شهر رو دور زدی و حالا تمام ربات‌ها به فرمان تو هستن!",
        "choices": [{"text": "شروع دوباره ماجراجویی", "next": "start"}]
    },
    "future_fly_danger": {
        "theme": "future",
        "title": "پرواز بی‌سرانجام",
        "text": "پرشت بی‌محابا بود و نتونستی ماشین پرنده رو بگیری؛ سقوط آزاد به اعماق شهر...",
        "choices": [{"text": "تلاش مجدد در زمان", "next": "start"}]
    },
    "future_mars_win": {
        "theme": "future",
        "title": "نجات کلونی مریخ",
        "text": "در آخرین لحظه مخزن اکسیژن رو تعمیر کردی و کل انسان‌های مریخ رو نجات دادی!",
        "choices": [{"text": "شروع دوباره ماجراجویی", "next": "start"}]
    },
    "future_escape_pod": {
        "theme": "future",
        "title": "سرگردان در فضا",
        "text": "سفینه نجات پرتاب شد ولی سیستم هدایتش قفل شد و توی فضا سرگردان موندی...",
        "choices": [{"text": "تلاش مجدد در زمان", "next": "start"}]
    }
}

# لیست‌های تصادفی برای انتخاب رندوم داستان‌ها
PAST_POOL = ["middle_ages_1", "middle_ages_2"]
FUTURE_POOL = ["future_city_1", "future_city_2"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/step', methods=['POST'])
def step():
    data = request.get_json()
    step_id = data.get('step', 'start')
    
    # اگر کاربر دکمه‌ی سفر رندوم به گذشته یا آینده رو زد، یکی رو تصادفی انتخاب کن!
    if step_id == 'random_past':
        step_id = random.choice(PAST_POOL)
    elif step_id == 'random_future':
        step_id = random.choice(FUTURE_POOL)
        
    current_node = STORY.get(step_id, STORY['start'])
    return jsonify(current_node)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
