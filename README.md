# Telegram AI bot for Bali

Telegram-бот, который:
- показывает погоду на Бали и дает советы по одежде,
- отправляет ежедневную погодную сводку,
- отвечает на любой обычный текст через Claude (Anthropic),
- поддерживает контекст диалога и потоковый вывод ответа.

## 1) Требования

- Python 3.10+
- Telegram bot token от [@BotFather](https://t.me/BotFather)
- Anthropic API key

## 2) Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Настройка окружения

Скопируй `.env.example` в `.env` и заполни значения:

```bash
cp .env.example .env
```

Минимально обязательные:
- `TELEGRAM_BOT_TOKEN`
- `ANTHROPIC_API_KEY`

Ключевые настройки LLM:
- `LLM_MODEL` (например, `claude-3-5-haiku-latest`)
- `LLM_TEMPERATURE`
- `LLM_MAX_TOKENS`
- `LLM_TIMEOUT_SECONDS`

Бюджет и контекст:
- `DAILY_BUDGET_USD` (по умолчанию `2.0`)
- `BUDGET_TIMEZONE`
- `CONTEXT_MAX_TURNS`
- `STREAM_EDIT_INTERVAL_MS`

## 4) Запуск

```bash
python bot.py
```

## 5) Поведение в Telegram

- `/start` — приветствие и список команд
- `/weather` — текущая погода + совет по одежде
- `/dailyon` — включить ежедневную сводку в 08:00 (время Бали)
- `/dailyoff` — выключить ежедневную сводку
- Любой текст без `/` — AI-ответ от Claude с учетом контекста

## 6) Ограничение бюджета

- Бот считает примерную стоимость по токенам входа/выхода.
- Когда дневной лимит (`DAILY_BUDGET_USD`) достигнут, AI-ответы отключаются до следующего дня.
- Погодные команды продолжают работать.

## 7) Тесты

```bash
pytest
```
