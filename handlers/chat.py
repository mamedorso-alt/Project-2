import logging
import time

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from services.budget_service import BudgetService
from services.context_store import ContextStore
from services.llm_service import LLMService

logger = logging.getLogger(__name__)


async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_text = update.message.text.strip()
    if not user_text:
        return

    llm: LLMService = context.application.bot_data["llm_service"]
    store: ContextStore = context.application.bot_data["context_store"]
    budget: BudgetService = context.application.bot_data["budget_service"]
    stream_interval = context.application.bot_data["stream_edit_interval_ms"] / 1000
    max_output_chars = context.application.bot_data["llm_max_output_chars"]

    if not budget.can_spend():
        await update.message.reply_text(
            "Дневной лимит AI-ответов достигнут. Попробуй снова завтра."
        )
        return

    store.add_user(chat_id, user_text)
    messages = store.get_messages(chat_id)

    placeholder = await update.message.reply_text("Думаю...")
    last_edit = time.monotonic()
    last_sent_text = "Думаю..."
    final_text = ""

    try:
        async def on_chunk(partial_text: str) -> None:
            nonlocal last_edit, last_sent_text
            now = time.monotonic()
            if (
                now - last_edit >= stream_interval
                and partial_text.strip()
                and partial_text != last_sent_text
            ):
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=placeholder.message_id,
                        text=partial_text,
                    )
                    last_sent_text = partial_text
                    last_edit = now
                except BadRequest as edit_err:
                    if "Message is not modified" not in str(edit_err):
                        raise

        final_text, usage = await llm.stream_answer(messages, on_chunk=on_chunk)

        if final_text:
            final_text = final_text.strip()
            if len(final_text) > max_output_chars:
                final_text = final_text[: max_output_chars - 1].rstrip() + "…"
            if final_text != last_sent_text:
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=placeholder.message_id,
                        text=final_text,
                    )
                    last_sent_text = final_text
                except BadRequest as edit_err:
                    if "Message is not modified" not in str(edit_err):
                        raise
        else:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=placeholder.message_id,
                text="Пустой ответ от модели. Попробуй переформулировать вопрос.",
            )

        cost = budget.register_usage(usage.input_tokens, usage.output_tokens)
        logger.info(
            "chat_id=%s input_tokens=%s output_tokens=%s cost=%.6f spent_today=%.6f",
            chat_id,
            usage.input_tokens,
            usage.output_tokens,
            cost,
            budget.spent_today(),
        )
        if final_text:
            store.add_assistant(chat_id, final_text)
    except Exception as err:
        logger.exception("LLM chat failed for chat_id=%s: %s", chat_id, err)
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=placeholder.message_id,
            text="Сейчас не получается ответить через AI. Попробуй еще раз чуть позже.",
        )
