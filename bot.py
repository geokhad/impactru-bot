from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import random, datetime, os, asyncio
from scheduler import setup_scheduler
from utils.google_sheets import save_feedback_to_google_sheets
from utils.subscriber_sheet import save_subscriber_to_sheet
from utils.subscriber_stats import get_subscriber_count
import nest_asyncio
import openai
from openai import OpenAI
from utils.usage_tracker import check_and_increment_usage




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
    user = update.effective_user
    args = context.args

    try:
        save_subscriber_to_sheet(user.id, user.full_name, user.username)
    except Exception as e:
        print("Ошибка при сохранении в Google Sheets:", e)

    if args:
        if args[0] == "feedback":
            await update.message.reply_text("✍️ Напишите отзыв в формате:\n/feedback ваш текст")
            return
        elif args[0] == "share":
            await update.message.reply_text("🙏 Спасибо, что делитесь ботом с другими!")
            return

    await update.message.reply_text("Привет! Я твой бот 😊 Напиши /help чтобы узнать, что я умею.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start — запустить бота\n"
        "/help — список команд\n"
        "/post <текст> — отправить пост в канал\n"
        "/feedback <текст> — отзыв\n"
        "/quote — цитата дня\n"
        "/poll Вопрос Вариант1 Вариант2 [...] — опрос\n"
        "/menu — меню с кнопками\n"
        "/subscribers — количество подписчиков"
    )
    await update.message.reply_text(help_text)

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Нет доступа.")
        return

    message = ' '.join(context.args) or "📣 Маленький шаг — большое дело"

    keyboard = [
        [InlineKeyboardButton("🔗 Подробнее", url="https://t.me/Impactru")],
        [InlineKeyboardButton("📢 Поделиться ботом", url="https://t.me/MyblogPR_bot?start=share")],
        [InlineKeyboardButton("📝 Оставить отзыв", url="https://t.me/MyblogPR_bot?start=feedback")]
    ]
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

async def subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Только для администратора.")
        return

    try:
        count = get_subscriber_count()
        await update.message.reply_text(f"👥 Всего подписчиков: {count}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
        
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = ' '.join(context.args)
    if not user_input:
        allowed, remaining = check_and_increment_usage(update.effective_user.id)
    if not allowed:
        await update.message.reply_text("🚫 Лимит: не более 5 GPT-запросов в день.")
        return

    await update.message.reply_text(f"💬 Осталось GPT-запросов сегодня: {remaining}")

        await update.message.reply_text("❓ Введите вопрос после команды /ask")
        return

    await update.message.reply_text("💬 Думаю...")

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # или gpt-4, если есть доступ
            messages=[
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        answer = response.choices[0].message.content.strip()
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка от OpenAI:\n{e}")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("post", post))
app.add_handler(CommandHandler("feedback", feedback))
app.add_handler(CommandHandler("quote", quote))
app.add_handler(CommandHandler("poll", poll))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("subscribers", subscribers))
app.add_handler(CommandHandler("ask", ask))



print("✅ Бот запущен через Webhook.")

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
