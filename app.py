from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# داستان‌ها و دوره‌های زمانی به همراه انتخاب‌ها و تغییرات تم
STORY_DATA = {
    "start": {
        "era": "آزمایشگاه زمان (حال)",
        "theme": "modern",
        "text": "تو وسط یک آزمایشگاه تاریک ایستادی. روبه‌روت ماشین زمان روشن است. کدام دکمه را می‌فشاری؟",
        "choices": [
            {"text": "سفر به مصر باستان (مقبره فراعنه)", "next": "egypt"},
            {"text": "سفر به آینده سایبرپانک (سال ۲۱۵۰)", "next": "cyberpunk"}
        ]
    },
    "egypt": {
        "era": "مصر باستان - مقبره توت‌عنخ‌آمون",
        "theme": "egypt",
        "text": "درون یک مقبره تاریک گیر افتادی. روی دیوار دو اهرم سنگی با نماد هیروگلیف هست. کدام را می‌کشی؟",
        "choices": [
            {"text": "اهرم با نماد چشم هورس (چپ)", "next": "egypt_win"},
            {"text": "اهرم با نماد مار سمی (راست)", "next": "game_over"}
        ]
    },
    "cyberpunk": {
        "era": "آینده سایبرپانک - نئون سیتی",
        "theme": "cyberpunk",
        "text": "سیستم امنیتی شهر قفل شده و آلارم به صدا دراومده! برای عبور از فایروال چه می‌کنی؟",
        "choices": [
            {"text": "تزریق کد هک سریع به ترمینال مرکزی", "next": "cyber_win"},
            {"text": "قطع کردن کابل اصلی برق شهر", "next": "game_over"}
        ]
    },
    "egypt_win": {
        "era": "پیروزی در مصر!",
        "theme": "egypt",
        "text": "آفرین! در مخفی باز شد و گنجینه زمان رو پیدا کردی. تو برنده این مرحله شدی! 🎉",
        "choices": [{"text": "شروع دوباره سفر", "next": "start"}]
    },
    "cyber_win": {
        "era": "پیروزی سایبرپانک!",
        "theme": "cyberpunk",
        "text": "فایروال هک شد! تو شبکه شهر رو نجات دادی و قهرمان آینده شدی! ⚡",
        "choices": [{"text": "شروع دوباره سفر", "next": "start"}]
    },
    "game_over": {
        "era": "پارادوکس زمانی!",
        "theme": "gameover",
        "text": "اشتباه مرگبار! زمان منقطع شد و تو در تاریخ گم شدی... 💀",
        "choices": [{"text": "تلاش مجدد", "next": "start"}]
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_node', methods=['POST'])
def get_node():
    data = request.get_json()
    node_id = data.get('node', 'start')
    node_info = STORY_DATA.get(node_id, STORY_DATA['start'])
    return jsonify(node_info)

if __name__ == '__main__':
    app.run(debug=True)
