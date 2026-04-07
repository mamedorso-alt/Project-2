from dataclasses import dataclass
from typing import Awaitable, Callable

from anthropic import AsyncAnthropic

from core.config import Settings


@dataclass
class LLMUsage:
    input_tokens: int
    output_tokens: int


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    def system_prompt(self) -> str:
        return (
            "You are a helpful Telegram assistant. "
            "Answer in the user's language. Keep answers concise but useful."
        )

    async def stream_answer(
        self,
        context_messages: list[dict[str, str]],
        on_chunk: Callable[[str], Awaitable[None]] | None = None,
    ) -> tuple[str, LLMUsage]:
        chunks: list[str] = []
        async with self.client.messages.stream(
            model=self.settings.llm_model,
            max_tokens=self.settings.llm_max_tokens,
            temperature=self.settings.llm_temperature,
            system=self.system_prompt(),
            messages=context_messages,
            timeout=self.settings.llm_timeout_seconds,
        ) as stream:
            async for text in stream.text_stream:
                chunks.append(text)
                if on_chunk is not None:
                    await on_chunk("".join(chunks))
            final_message = await stream.get_final_message()

        return "".join(chunks), LLMUsage(
            input_tokens=final_message.usage.input_tokens,
            output_tokens=final_message.usage.output_tokens,
        )
