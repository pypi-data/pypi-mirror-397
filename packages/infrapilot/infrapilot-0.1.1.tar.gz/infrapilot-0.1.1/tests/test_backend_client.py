from __future__ import annotations

from infrapilot_cli.backend.client import BackendClient


def _make_client() -> BackendClient:
    return object.__new__(BackendClient)  # type: ignore[call-arg]


def test_extract_ai_messages_from_nested_payload() -> None:
    client = _make_client()
    payload = {
        "event": "updates",
        "data": {
            "node": "response",
            "value": {
                "messages": [
                    {
                        "type": "ai",
                        "content": [
                            {"type": "text", "text": "Hello"},
                            {"type": "text", "text": "InfraPilot"},
                        ],
                    },
                    {"type": "tool", "content": "ignore-me"},
                ]
            },
        },
    }

    assert client._extract_ai_messages(payload) == ["Hello\nInfraPilot"]


def test_extract_ai_messages_handles_plain_message_dicts() -> None:
    client = _make_client()
    payload = {
        "event": "messages",
        "data": {
            "responses": [
                {"type": "assistant", "content": "First"},
                {"type": "ai", "content": {"text": "Second"}},
                {"type": "human", "content": "ignore"},
            ]
        },
    }

    assert client._extract_ai_messages(payload) == ["First", "Second"]


def test_extract_ai_messages_reads_list_wrapped_chunks() -> None:
    client = _make_client()
    payload = [
        "messages",
        {
            "messages": [
                {
                    "type": "assistant",
                    "content": [{"type": "text", "text": "Stream ready."}],
                }
            ]
        },
    ]

    assert client._extract_ai_messages(payload) == ["Stream ready."]
