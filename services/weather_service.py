import logging
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BALI_LAT = -8.65
BALI_LON = 115.2167
TIMEZONE = "Asia/Makassar"


async def _from_wttr_fallback(timeout_seconds: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.get("https://wttr.in/Denpasar?format=j1")
        response.raise_for_status()
        data = response.json()

    current = data["current_condition"][0]
    today = data["weather"][0]
    now_hour = datetime.utcnow().hour
    hourly = today.get("hourly", [])
    closest = min(
        hourly,
        key=lambda item: abs(int(item.get("time", "0")) // 100 - now_hour),
        default={},
    )

    return {
        "temperature": float(current["temp_C"]),
        "humidity": int(current["humidity"]),
        "weather_code": int(current.get("weatherCode", 3)),
        "wind": float(current["windspeedKmph"]),
        "temp_max": float(today["maxtempC"]),
        "temp_min": float(today["mintempC"]),
        "rain_probability": int(closest.get("chanceofrain", 0)),
    }


async def fetch_weather(timeout_seconds: int = 12) -> dict[str, Any]:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={BALI_LAT}"
        f"&longitude={BALI_LON}"
        "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone={TIMEZONE}"
    )

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as err:
        logger.warning("Open-Meteo unavailable, using wttr.in fallback: %s", err)
        return await _from_wttr_fallback(timeout_seconds=timeout_seconds)

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


def clothing_advice(weather: dict[str, Any]) -> str:
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


def build_weather_message(weather: dict[str, Any]) -> str:
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
