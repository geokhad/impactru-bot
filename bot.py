from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import random, datetime
from scheduler import setup_scheduler
from utils.google_sheets import save_feedback_to_google_sheets

import os
TOKEN = os.environ["TOKEN"]

ALLOWED_USERS = [671003971]
CHANNEL_ID = "@Impactru"
QUOTES = [
    "Будь собой. Прочие роли уже заняты. — Оскар Уайльд",
    "Если не сейчас — то когда?",
    "Секрет вперёд — начать. — Марк Твен",
    "Делай, что можешь, с тем, что имеешь, там, где ты есть. — Теодор Рузвельт",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой бот 😊 Напиши /help чтобы узнать, что я умею.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start — запустить бота\n"
        "/help — список команд\n"
        "/post <текст> — отправить пост в канал\n"
        "/feedback <текст> — отзыв\n"
        "/quote — цитата дня\n"
        "/poll Вопрос Вариант1 Вариант2 [...] — опрос"
    )
    await update.message.reply_text(help_text)

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Нет доступа.")
        return
    message = ' '.join(context.args) or "📣 Маленький шаг — большое дело"
    keyboard = [[InlineKeyboardButton("Подробнее", url="https://t.me/Impactru")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    await update.message.reply_text("✅ Сообщение отправлено в канал.")

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback_text = ' '.join(context.args)
    if not feedback_text:
        await update.message.reply_text("Напишите текст отзыва после /feedback.")
        return

    user = update.message.from_user

    try:
        save_feedback_to_google_sheets(user.full_name, str(user.id), feedback_text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка Google Sheets:\n{e}")
        print("❌ Ошибка Google Sheets:", e)
        return

    with open("feedback.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {user.full_name} ({user.id}): {feedback_text}\n")

    await update.message.reply_text("Спасибо за ваш отзыв!")

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🧠 Цитата дня:\n{random.choice(QUOTES)}")

async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Нет доступа.")
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Формат: /poll Вопрос Вариант1 Вариант2 ...")
        return
    question = args[0]
    options = args[1:]
    await context.bot.send_poll(chat_id=CHANNEL_ID, question=question, options=options, is_anonymous=False)
    await update.message.reply_text("📊 Опрос отправлен в канал.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("post", post))
app.add_handler(CommandHandler("feedback", feedback))
app.add_handler(CommandHandler("quote", quote))
app.add_handler(CommandHandler("poll", poll))
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Поделиться ботом", url="https://t.me/MyblogPR_bot?start=share")],
        [InlineKeyboardButton("📝 Оставить отзыв", url="https://t.me/MyblogPR_bot?start=feedback")],
        [InlineKeyboardButton("📚 Наш канал", url="https://t.me/Impactru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔘 Выберите, что хотите сделать:",
        reply_markup=reply_markup
    )


print("✅ Бот запущен через Webhook.")

import asyncio
import nest_asyncio

nest_asyncio.apply()

async def main():
    setup_scheduler(app)
    await app.bot.set_webhook("https://impactru-bot.onrender.com")
    await app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url="https://impactru-bot.onrender.com"
    )

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

