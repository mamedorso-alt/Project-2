from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    anthropic_api_key: str
    llm_model: str
    llm_temperature: float
    llm_max_tokens: int
    llm_timeout_seconds: int
    daily_budget_usd: float
    budget_timezone: str
    context_max_turns: int
    stream_edit_interval_ms: int
    log_level: str
    model_input_cost_per_1m_tokens_usd: float
    model_output_cost_per_1m_tokens_usd: float


def load_settings() -> Settings:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не найден. Создай .env на основе .env.example.")

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY не найден. Добавь ключ в .env.")

    return Settings(
        telegram_bot_token=token,
        anthropic_api_key=anthropic_api_key,
        llm_model=os.getenv("LLM_MODEL", "claude-3-5-haiku-latest"),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.6")),
        llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "450")),
        llm_timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        daily_budget_usd=float(os.getenv("DAILY_BUDGET_USD", "2.0")),
        budget_timezone=os.getenv("BUDGET_TIMEZONE", "UTC"),
        context_max_turns=int(os.getenv("CONTEXT_MAX_TURNS", "8")),
        stream_edit_interval_ms=int(os.getenv("STREAM_EDIT_INTERVAL_MS", "1200")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        model_input_cost_per_1m_tokens_usd=float(
            os.getenv("MODEL_INPUT_COST_PER_1M_TOKENS_USD", "0.25")
        ),
        model_output_cost_per_1m_tokens_usd=float(
            os.getenv("MODEL_OUTPUT_COST_PER_1M_TOKENS_USD", "1.25")
        ),
    )
