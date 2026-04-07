from services.context_store import ContextStore


def test_context_store_keeps_recent_messages() -> None:
    store = ContextStore(max_turns=1)
    store.add_user(1, "hello")
    store.add_assistant(1, "hi")
    store.add_user(1, "new")

    messages = store.get_messages(1)
    assert len(messages) == 2
    assert messages[-1]["content"] == "new"
