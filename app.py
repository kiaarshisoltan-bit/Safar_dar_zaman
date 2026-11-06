import os
import time
import threading
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "").strip()
WEB_APP_URL = os.environ.get(
    "WEB_APP_URL", "https://safar-dar-zaman.onrender.com"
).strip()

BALE_BASE = "https://tapi.bale.ai"

# ---------------------------------------------------------------
# داستان‌ها (همان‌هایی که قبلاً داشتیم؛ اگر بلندترشان داری، جایگزین کن)
# ---------------------------------------------------------------
PAST_POOL = [
    "به سال ۱۲۵۰ خورشیدی رسیدی. هوای بازار پر از بوی نان و ادویه است...",
    "در کوچه‌های تخت جمشید قدم می‌زنی. سنگ‌تراش‌ها مشغول کارند...",
    "به دوران صفویه پرتاب شدی. میدان نقش جهان پر از جمعیت است...",
]

FUTURE_POOL = [
    "به سال ۲۱۴۰ رسیدی. شهرها زیر گنبدهای شیشه‌ای نفس می‌کشند...",
    "در ایستگاه مداری زمین، پنجره‌ها به سمت سیاره آبی باز می‌شوند...",
    "به شهری رسیدی که ماشین‌ها پرواز می‌کنند و درخت‌ها روی پشت‌بام‌ها رشد می‌کنند...",
]

import random

# ---------------------------------------------------------------
# وب (فلاسک)
# ---------------------------------------------------------------
@app.route("/")
def index():
    return render_template(
        "index.html",
        past_story=random.choice(PAST_POOL),
        future_story=random.choice(FUTURE_POOL),
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/story/<period>")
def api_story(period):
    if period == "past":
        return jsonify({"story": random.choice(PAST_POOL)})
    if period == "future":
        return jsonify({"story": random.choice(FUTURE_POOL)})
    return jsonify({"error": "unknown period"}), 400


# ---------------------------------------------------------------
# بله (پولینگ مستقیم با requests، بدون telebot)
# ---------------------------------------------------------------
def bale_call(method, payload=None, timeout=35):
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

    url = f"{BALE_BASE}/bot{TOKEN}/{method}"
    response = requests.post(url, json=payload or {}, timeout=timeout)

    # لاگ کامل برای عیب‌یابی (توکن در URL است، پس URL را چاپ نکن)
    print(f"[Bale] {method} -> HTTP {response.status_code} | {response.text[:400]}")

    response.raise_for_status()
    data = response.json()
    if not data.get("ok", False):
        raise RuntimeError(f"Bale API error: {data}")
    return data.get("result")


def send_start_message(chat_id):
    payload = {
        "chat_id": chat_id,
        "text": (
            "سلام کیا جان! 🤖✨\n"
            "دنیای سفر در زمان آماده است.\n"
            "برای ورود به نسخه‌ی گرافیکی و شروع ماجراجویی، روی دکمه‌ی زیر بزن:"
        ),
        "reply_markup": {
            "inline_keyboard": [[
                {
                    "text": "⏳ ورود به پورتال سفر در زمان",
                    "web_app": {"url": WEB_APP_URL},
                }
            ]]
        },
    }
    bale_call("sendMessage", payload)


def handle_update(update):
    message = update.get("message") or {}
    text = (message.get("text") or "").strip()
    chat_id = (message.get("chat") or {}).get("id")

    if not chat_id or not text:
        return

    command = text.split(maxsplit=1)[0].lower()

    if command == "/start":
        send_start_message(chat_id)
    elif command == "/help":
        bale_call("sendMessage", {
            "chat_id": chat_id,
            "text": "دستورها:\n/start شروع بازی\n/help راهنما",
        })


def run_bale_polling():
    if not TOKEN:
        print("❌ BOT_TOKEN در Environment تنظیم نشده است. پولینگ اجرا نمی‌شود.")
        return

    # اگر قبلاً وبهوک ثبت شده، باید حذف شود وگرنه getUpdates خطا می‌دهد
    try:
        bale_call("deleteWebhook", {})
        print("✅ وبهوک (در صورت وجود) حذف شد.")
    except Exception as e:
        print("⚠️ حذف وبهوک ناموفق:", repr(e))

    offset = None
    print("🤖 پولینگ بله شروع شد...")

    while True:
        try:
            payload = {"timeout": 25, "limit": 50}
            if offset is not None:
                payload["offset"] = offset

            updates = bale_call("getUpdates", payload, timeout=35) or []

            for update in updates:
                offset = update["update_id"] + 1
                try:
                    handle_update(update)
                except Exception as e:
                    print("❌ خطا در پردازش آپدیت:", repr(e))

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status == 401:
                print(
                    "❌ خطای 401 Unauthorized: توکن بله معتبر نیست یا مال "
                    "بات دیگری است. BOT_TOKEN را در Render بررسی/تعویض کن."
                )
                time.sleep(60)
            elif status == 409:
                print("❌ خطای 409: احتمالاً نمونه‌ی دیگری از سرویس در حال پولینگ است.")
                time.sleep(15)
            else:
                print("❌ خطای HTTP در پولینگ:", status, e)
                time.sleep(5)

        except Exception as e:
            print("❌ خطا در حلقه‌ی پولینگ:", repr(e))
            time.sleep(5)


# ---------------------------------------------------------------
# پینگ داخلی که Render را بیدار نگه می‌دارد
# ---------------------------------------------------------------
def self_ping():
    time.sleep(20)
    while True:
        try:
            requests.get(f"{WEB_APP_URL}/health", timeout=10)
        except Exception:
            pass
        time.sleep(600)  # هر ۱۰ دقیقه


def start_background_threads():
    threading.Thread(target=run_bale_polling, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()


# گارد برای جلوگیری از اجرای دوباره در حالت reload
if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    start_background_threads()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
