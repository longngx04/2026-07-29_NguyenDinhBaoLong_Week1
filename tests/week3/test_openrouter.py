import json
import urllib.error
from unittest.mock import MagicMock, patch
import pytest

from week3.config import AppConfig
from week3.llm.base import AnalysisPacket
from week3.llm.factory import build_llm
from week3.llm.fake import FakeLLM
from week3.llm.openrouter import OpenRouterClient, _sanitize_error


def _ok_body(content_obj):
    return json.dumps({
        "id": "gen-test-123",
        "model": "deepseek/deepseek-v4-flash-0731",
        "choices": [{"message": {"role": "assistant", "content": json.dumps(content_obj)}}],
        "usage": {"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40},
    }).encode("utf-8")


def test_openrouter_posts_expected_payload(monkeypatch):
    client = OpenRouterClient(
        api_key="sk-secret-key-12345",
        base_url="https://openrouter.ai/api/v1",
        model="deepseek/deepseek-v4-flash-0731",
        timeout_seconds=5.0,
        max_retries=1,
    )
    packet = AnalysisPacket(group_key="g1", finding_group={"source_finding_ids": ["f1"]})
    captured = {}

    class Resp:
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def read(self):
            return _ok_body({"schema_version": "1.0", "group_key": "g1"})
        status = 200

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.header_items()) if hasattr(req, "header_items") else {
            k: v for k, v in req.headers.items()
        }
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return Resp()

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = client.analyze(packet, system_prompt="SYS PROMPT")

    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert captured["body"]["model"] == "deepseek/deepseek-v4-flash-0731"
    assert captured["body"]["temperature"] == 0
    assert captured["body"]["response_format"] == {"type": "json_object"}
    assert captured["body"]["messages"][0] == {"role": "system", "content": "SYS PROMPT"}
    assert result.error is None
    assert result.parsed_response["group_key"] == "g1"
    assert result.request_id == "gen-test-123"
    assert result.prompt_tokens == 15
    assert result.completion_tokens == 25
    assert result.total_tokens == 40
    assert "sk-secret-key-12345" not in (result.error or "")


def test_missing_api_key_does_not_call_network():
    client = OpenRouterClient(
        api_key="",
        base_url="https://openrouter.ai/api/v1",
        model="deepseek/deepseek-v4-flash-0731",
        timeout_seconds=5.0,
        max_retries=1
    )
    with patch("urllib.request.urlopen") as mocked:
        with pytest.raises(ValueError, match="LLM_API_KEY is required"):
            client.analyze(AnalysisPacket(group_key="g1"), system_prompt="SYS")
        mocked.assert_not_called()


def test_retries_once_on_http_500():
    client = OpenRouterClient(
        api_key="sk-secret-key",
        base_url="https://openrouter.ai/api/v1",
        model="deepseek/deepseek-v4-flash-0731",
        max_retries=1
    )
    packet = AnalysisPacket(group_key="g1")

    class Resp:
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def read(self):
            return _ok_body({"schema_version": "1.0", "group_key": "g1"})

    call_count = 0

    def fake_urlopen(req, timeout=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise urllib.error.HTTPError(
                url=req.full_url, code=500, msg="Internal Server Error", hdrs={}, fp=None
            )
        return Resp()

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        with patch("time.sleep"):  # Speed up tests
            result = client.analyze(packet, system_prompt="SYS")

    assert call_count == 2
    assert result.error is None
    assert result.parsed_response["group_key"] == "g1"


def test_no_retry_on_http_400():
    client = OpenRouterClient(
        api_key="sk-secret-key-400",
        base_url="https://openrouter.ai/api/v1",
        model="deepseek/deepseek-v4-flash-0731",
        max_retries=1
    )
    packet = AnalysisPacket(group_key="g1")

    call_count = 0

    def fake_urlopen(req, timeout=None):
        nonlocal call_count
        call_count += 1
        raise urllib.error.HTTPError(
            url=req.full_url, code=400, msg="Bad Request with sk-secret-key-400 inside", hdrs={}, fp=None
        )

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = client.analyze(packet, system_prompt="SYS")

    assert call_count == 1
    assert result.error is not None
    assert "HTTP Error 400" in result.error
    assert "sk-secret-key-400" not in result.error
    assert "[REDACTED_API_KEY]" in result.error or "sk-secret-key-400" not in result.error


def test_provider_factory_openrouter(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("LLM_API_KEY", "sk-test-secret")
    config = AppConfig.from_env()
    llm = build_llm(config)
    assert isinstance(llm, OpenRouterClient)


def test_provider_factory_fake(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    config = AppConfig.from_env()
    llm = build_llm(config)
    assert isinstance(llm, FakeLLM)


def test_sanitize_error_redacts_api_key():
    key = "sk-openrouter-secret-key"
    msg = f"Failed connecting with Auth Bearer {key} to server"
    sanitized = _sanitize_error(msg, key)
    assert key not in sanitized
    assert "[REDACTED_API_KEY]" in sanitized
