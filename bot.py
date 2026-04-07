import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from core.config import load_settings
from core.logging_setup import setup_logging
from handlers.chat import chat_message
from handlers.commands import daily_off, daily_on, start, weather
from services.budget_service import BudgetService
from services.context_store import ContextStore
from services.llm_service import LLMService


def main() -> None:
    settings = load_settings()
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.bot_data["llm_service"] = LLMService(settings)
    app.bot_data["context_store"] = ContextStore(max_turns=settings.context_max_turns)
    app.bot_data["budget_service"] = BudgetService(
        daily_budget_usd=settings.daily_budget_usd,
        timezone_name=settings.budget_timezone,
        input_cost_per_1m=settings.model_input_cost_per_1m_tokens_usd,
        output_cost_per_1m=settings.model_output_cost_per_1m_tokens_usd,
    )
    app.bot_data["stream_edit_interval_ms"] = settings.stream_edit_interval_ms
    app.bot_data["llm_max_output_chars"] = settings.llm_max_output_chars

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("dailyon", daily_on))
    app.add_handler(CommandHandler("dailyoff", daily_off))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
