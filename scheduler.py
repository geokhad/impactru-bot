from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.constants import ParseMode

def setup_scheduler(app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        lambda: app.bot.send_message(chat_id='@Impactru', text='⏰ Автопостинг: не забудьте про эфир сегодня!', parse_mode=ParseMode.HTML),
        CronTrigger(hour=10, minute=0)
    )
    scheduler.start()
