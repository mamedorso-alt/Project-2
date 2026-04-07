from collections import defaultdict, deque
from typing import Deque


class ContextStore:
    def __init__(self, max_turns: int) -> None:
        self.max_turns = max_turns
        self._messages: dict[int, Deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=max_turns * 2)
        )

    def add_user(self, chat_id: int, text: str) -> None:
        self._messages[chat_id].append({"role": "user", "content": text})

    def add_assistant(self, chat_id: int, text: str) -> None:
        self._messages[chat_id].append({"role": "assistant", "content": text})

    def get_messages(self, chat_id: int) -> list[dict[str, str]]:
        return list(self._messages[chat_id])
