import logging
import os
from datetime import time
from typing import Dict, Any

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Bali (Denpasar) coordinates
BALI_LAT = -8.65
BALI_LON = 115.2167
TIMEZONE = "Asia/Makassar"
DAILY_JOB_NAME = "daily_weather_message"


def fetch_weather() -> Dict[str, Any]:
    """Fetch current weather and daily max/min from Open-Meteo."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={BALI_LAT}"
        f"&longitude={BALI_LON}"
        "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone={TIMEZONE}"
    )

    response = requests.get(url, timeout=12)
    response.raise_for_status()
    data = response.json()

    current = data["current"]
    daily = data["daily"]

    return {
        "temperature": float(current["temperature_2m"]),
        "humidity": int(current["relative_humidity_2m"]),
        "weather_code": int(current["weather_code"]),
        "wind": float(current["wind_speed_10m"]),
        "temp_max": float(daily["temperature_2m_max"][0]),
        "temp_min": float(daily["temperature_2m_min"][0]),
        "rain_probability": int(daily["precipitation_probability_max"][0]),
    }


def weather_description(weather_code: int) -> str:
    code_map = {
        0: "ясно",
        1: "преимущественно ясно",
        2: "переменная облачность",
        3: "пасмурно",
        45: "туман",
        48: "изморозь и туман",
        51: "слабая морось",
        53: "морось",
        55: "сильная морось",
        61: "слабый дождь",
        63: "дождь",
        65: "сильный дождь",
        71: "слабый снег",
        73: "снег",
        75: "сильный снег",
        80: "ливневый дождь",
        81: "ливень",
        82: "сильный ливень",
        95: "гроза",
        96: "гроза с градом",
        99: "сильная гроза с градом",
    }
    return code_map.get(weather_code, "погода меняется")


def clothing_advice(weather: Dict[str, Any]) -> str:
    temp = weather["temperature"]
    rain = weather["rain_probability"]
    wind = weather["wind"]
    tips = []

    if temp >= 31:
        tips.append("очень жарко: легкая футболка/майка и шорты")
    elif temp >= 27:
        tips.append("тепло: футболка и легкие брюки или шорты")
    elif temp >= 24:
        tips.append("комфортно: футболка, можно взять тонкую рубашку")
    else:
        tips.append("прохладнее обычного для Бали: легкая кофта пригодится")

    if rain >= 60:
        tips.append("высокий шанс дождя: возьми дождевик или зонт")
    elif rain >= 35:
        tips.append("возможен дождь: лучше взять компактный зонт")

    if wind >= 20:
        tips.append("ветрено: на байке добавь легкую ветровку")

    tips.append("не забудь солнцезащитный крем и воду")
    return "; ".join(tips)


def build_weather_message(weather: Dict[str, Any]) -> str:
    description = weather_description(weather["weather_code"])
    advice = clothing_advice(weather)
    return (
        "Привет! Вот погода на Бали сейчас:\n"
        f"- Состояние: {description}\n"
        f"- Температура: {weather['temperature']}°C "
        f"(днем до {weather['temp_max']}°C, ночью до {weather['temp_min']}°C)\n"
        f"- Влажность: {weather['humidity']}%\n"
        f"- Ветер: {weather['wind']} км/ч\n"
        f"- Вероятность дождя сегодня: {weather['rain_probability']}%\n\n"
        f"Что надеть: {advice}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Привет! Я твой погодный бот для Бали.\n"
        "Команды:\n"
        "/weather - погода и рекомендации по одежде\n"
        "/dailyon - ежедневное сообщение в 08:00\n"
        "/dailyoff - выключить ежедневные сообщения"
    )
    await update.message.reply_text(text)


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        info = fetch_weather()
        await update.message.reply_text(build_weather_message(info))
    except Exception as err:
        logger.exception("Weather fetch failed: %s", err)
        await update.message.reply_text(
            "Не получилось получить погоду. Попробуй еще раз через минуту."
        )


async def send_daily_weather(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    try:
        info = fetch_weather()
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


def main() -> None:
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN не найден. Создай .env на основе .env.example."
        )

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("dailyon", daily_on))
    app.add_handler(CommandHandler("dailyoff", daily_off))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
