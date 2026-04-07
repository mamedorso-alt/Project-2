import logging
from datetime import time

from telegram import Update
from telegram.ext import ContextTypes

from services.weather_service import build_weather_message, fetch_weather

logger = logging.getLogger(__name__)

DAILY_JOB_NAME = "daily_weather_message"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Привет! Я твой AI-бот для Бали.\n"
        "Команды:\n"
        "/weather - погода и рекомендации по одежде\n"
        "/dailyon - ежедневное сообщение в 08:00\n"
        "/dailyoff - выключить ежедневные сообщения"
    )
    await update.message.reply_text(text)


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        info = await fetch_weather()
        await update.message.reply_text(build_weather_message(info))
    except Exception as err:
        logger.exception("Weather fetch failed: %s", err)
        await update.message.reply_text(
            "Не получилось получить погоду. Попробуй еще раз через минуту."
        )


async def send_daily_weather(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    try:
        info = await fetch_weather()
        await context.bot.send_message(chat_id=chat_id, text=build_weather_message(info))
    except Exception as err:
        logger.exception("Daily weather send failed: %s", err)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Не смог отправить погоду сегодня утром, попробую позже по команде /weather.",
        )


async def daily_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    for job in context.job_queue.get_jobs_by_name(f"{DAILY_JOB_NAME}_{chat_id}"):
        job.schedule_removal()

    context.job_queue.run_daily(
        send_daily_weather,
        time=time(hour=8, minute=0, second=0),
        name=f"{DAILY_JOB_NAME}_{chat_id}",
        chat_id=chat_id,
    )
    await update.message.reply_text(
        "Готово! Буду присылать утреннюю сводку погоды каждый день в 08:00 (время Бали)."
    )


async def daily_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    jobs = context.job_queue.get_jobs_by_name(f"{DAILY_JOB_NAME}_{chat_id}")

    if not jobs:
        await update.message.reply_text("Ежедневная рассылка и так выключена.")
        return

    for job in jobs:
        job.schedule_removal()

    await update.message.reply_text("Ок, ежедневную рассылку отключил.")
