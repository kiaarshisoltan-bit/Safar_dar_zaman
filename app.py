import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# --- CORS: اجازه به همه دامنه‌ها (گیت‌هاب پیجز، لوکال و ...) ---
CORS(app, resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"], supports_credentials=False)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ---------------- داستان‌ها ----------------
STORIES = {
    "past": [
        {
            "title": "کوچه‌های بغداد، سال ۸۰۰ میلادی",
            "text": "بوی زعفران و چرم تازه توی هواست. مردی با عمامه‌ی آبی از کنارت رد می‌شود و چیزی روی زمین می‌اندازد...",
            "choices": ["شیء را بردار", "دنبال مرد برو", "بی‌تفاوت رد شو"],
        },
        {
            "title": "کاروانسرای جاده‌ی ابریشم",
            "text": "شب است و کاروانی خسته در کاروانسرا اتراق کرده. پیرمردی کنارت می‌نشیند و می‌گوید: «مسافری از آینده؟ عجیب...»",
            "choices": ["راستش را بگو", "دروغ بگو", "سکوت کن"],
        },
        {
            "title": "روزگار هخامنشیان",
            "text": "ستون‌های سنگی تخت جمشید بالای سرت قد کشیده‌اند. نگهبانی با نیزه به سمتت می‌آید و فریاد می‌زند...",
            "choices": ["فرار کن", "تسلیم شو", "با اشاره توضیح بده"],
        },
    ],
    "future": [
        {
            "title": "نئون‌شهر، سال ۲۱۴۰",
            "text": "باران اسیدی روی شیشه‌ی کلاه‌خودت می‌خورد. هوش مصنوعی شهر می‌پرسد: «شهروند ثبت‌نشده! هویتت؟»",
            "choices": ["هویت جعلی بساز", "واقعیت را بگو", "فرار کن"],
        },
        {
            "title": "ایستگاه مداری زحل",
            "text": "از پنجره، حلقه‌های زحل را می‌بینی. یک ربات تعمیرکار جلویت را سد کرده و می‌گوید: «بلیتت منقضی شده.»",
            "choices": ["بلیت را هک کن", "مذاکره کن", "از دریچه فرار کن"],
        },
        {
            "title": "زمین مرده، سال ۲۳۰۰",
            "text": "هیچ درختی نیست. فقط گرد و خاک و آسمان خاکستری. ردی از نور آبی تو را به سمت یک گنبد می‌کشاند...",
            "choices": ["وارد گنبد شو", "رد نور را دنبال کن", "برگرد به ماشین زمان"],
        },
    ],
}


def pick_story(era: str):
    pool = STORIES.get(era) or STORIES["past"]
    return random.choice(pool)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "پورتال زمان فعال است ⏳"})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/step", methods=["POST", "OPTIONS"])
def step():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    era = str(data.get("era", "past")).lower()
    if era not in STORIES:
        era = "past"

    story = pick_story(era)
    return jsonify({
        "era": era,
        "title": story["title"],
        "text": story["text"],
        "choices": story["choices"],
    })


@app.route("/api/start", methods=["POST", "OPTIONS"])
def start():
    if request.method == "OPTIONS":
        return ("", 204)
    return jsonify({
        "status": "ok",
        "eras": list(STORIES.keys()),
        "message": "سفر در زمان آغاز شد",
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
