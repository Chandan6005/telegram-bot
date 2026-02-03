import os
import datetime
from flask import Flask, request
from telegram import Bot, Update

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# ---------------- LOGIC ----------------
def check_data_usage(data: float) -> str:
    start_date = datetime.date(2025, 9, 17)
    today = datetime.date.today()

    days_used = (today - start_date).days
    total_data = 24

    if days_used < 0:
        return "Plan not started yet."

    allowed = (total_data / 365) * days_used
    spent = total_data - data
    remaining_days = max(365 - days_used, 1)

    per_day = data / remaining_days
    status = "✅ You're within limit" if spent <= allowed else "⚠️ Reduce usage"

    return (
        f"Days since start: {days_used}\n"
        f"Used data: {spent:.2f} GB\n"
        f"{status}\n"
        f"Allowed per day: {per_day:.2f} GB"
    )

# ---------------- WEBHOOK ----------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)

    if update.message and update.message.text:
        chat_id = update.message.chat_id
        text = update.message.text.strip()

        if text == "/start":
            bot.send_message(
                chat_id=chat_id,
                text="Hi 👋 Send remaining data in GB"
            )
        else:
            try:
                data = float(text)
                reply = check_data_usage(data)
                bot.send_message(chat_id=chat_id, text=reply)
            except ValueError:
                bot.send_message(
                    chat_id=chat_id,
                    text="Please send a valid number (GB)"
                )

    return "OK"

@app.route("/")
def index():
    return "Bot is running 🚀"
