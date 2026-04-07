# Telegram weather bot for Bali

Простой Telegram-бот, который:
- показывает текущую погоду на Бали (район Денпасара),
- дает рекомендации, как одеться,
- умеет слать ежедневную сводку утром.

## 1) Что нужно

- Python 3.10+
- Telegram bot token от [@BotFather](https://t.me/BotFather)

## 2) Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Настройка токена

Скопируй `.env.example` в `.env` и вставь свой токен:

```bash
cp .env.example .env
```

Файл `.env`:

```env
TELEGRAM_BOT_TOKEN=your_real_token_here
```

## 4) Запуск

```bash
python bot.py
```

## 5) Команды в Telegram

- `/start` - приветствие и список команд
- `/weather` - текущая погода + совет по одежде
- `/dailyon` - включить ежедневную сводку в 08:00 (время Бали)
- `/dailyoff` - выключить ежедневную сводку

## Как это работает

- Погода берется из Open-Meteo API.
- Координаты по умолчанию: Бали (Денпасар).
