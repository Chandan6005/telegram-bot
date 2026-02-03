import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)
import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

application = Application.builder().token(BOT_TOKEN).build()

# --- BOT LOGIC ---
def check_data_usage(data: float) -> str:
    start_date = datetime.date(2025, 9, 17)
    today = datetime.date.today()

    date_diff = (today - start_date).days
    total_data = 24

    allowed = (total_data / 365) * date_diff
    spent = total_data - data
    remaining_days = 365 - date_diff

    if remaining_days <= 0:
        return "❌ Plan expired"

    per_day = data / remaining_days

    status = "✅ You're within limit" if spent <= allowed else "⚠️ Reduce usage"

    return (
        f"Days since start: {date_diff}\n"
        f"Used data: {spent:.2f} GB\n"
        f"{status}\n"
        f"Allowed per day: {per_day:.2f} GB"
    )

# --- HANDLERS ---
async def start(update, context):
    await update.message.reply_text(
        "Hi 👋 Send remaining data in GB"
    )

async def handle_message(update, context):
    try:
        data = float(update.message.text)
        await update.message.reply_text(check_data_usage(data))
    except:
        await update.message.reply_text("Send a valid number")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- WEBHOOK ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK"

@app.route("/")
def index():
    return "Bot is alive 🚀"
