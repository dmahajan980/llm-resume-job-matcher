import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from llm.client import LLMClient

ROOT = Path(__file__).resolve().parents[1]


class FakeGroq:
    def __init__(self, api_key):
        self.api_key = api_key
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content='{"ok": true}')
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_chat_sends_json_mode_with_system_user_and_extra_messages(monkeypatch):
    monkeypatch.setattr("llm.client.Groq", FakeGroq)
    client = LLMClient(model="openai/gpt-oss-120b")
    history = [{"role": "assistant", "content": "{}"}]

    message = client.chat("system", "user", messages=history)

    assert client.client.api_key
    assert message.content == '{"ok": true}'
    call = client.client.calls[0]
    assert call["model"] == "openai/gpt-oss-120b"
    assert call["response_format"] == {"type": "json_object"}
    assert call["messages"] == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
        {"role": "assistant", "content": "{}"},
    ]


def test_chat_omits_extra_messages_when_none_are_given(monkeypatch):
    monkeypatch.setattr("llm.client.Groq", FakeGroq)
    client = LLMClient()

    client.chat("system", "user")
    client.chat("system", "user", messages=[])

    assert client.model == "openai/gpt-oss-20b"
    for call in client.client.calls:
        assert call["messages"] == [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "user"},
        ]


def test_import_fails_when_the_api_key_is_missing():
    env = os.environ.copy()
    env.pop("GROQ_API_KEY", None)
    script = """
import dotenv
dotenv.load_dotenv = lambda *args, **kwargs: None
import llm.client
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "GROQ_API_KEY is not set" in result.stderr


def test_groq_errors_propagate(monkeypatch):
    class ExplodingGroq(FakeGroq):
        def create(self, **kwargs):
            raise RuntimeError("token limit")

    monkeypatch.setattr("llm.client.Groq", ExplodingGroq)

    with pytest.raises(RuntimeError, match="token limit"):
        LLMClient().chat("system", "user")
