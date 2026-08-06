# OpenRouter Direct Analysis Implementation Plan

> **For agentic workers (Antigravity):** Execute this plan task-by-task. Follow `.agents/rules/role_coder.md` and `.agents/rules/coding_agent_rules.md`. Steps use checkbox (`- [ ]`) syntax for tracking. Do **not** call real OpenRouter from tests/CI.

**Goal:** Wire Week 3 real analysis runs to OpenRouter Chat Completions (`deepseek/deepseek-v4-flash-0731`) via direct stdlib HTTPS, while keeping `FakeLLM` for offline tests.

**Architecture:** Production path builds system prompt + `AnalysisPacket` JSON, POSTs to `https://openrouter.ai/api/v1/chat/completions`, parses assistant JSON, then reuses existing schema/provenance validation. Tests mock the HTTP boundary; CI never uses network or secrets.

**Tech Stack:** Python 3.10+, stdlib `urllib`/`http.client` (or equivalent stdlib HTTPS), existing `week3.llm.base` types, `pytest`, pydantic already in project.

**Design source of truth:** `docs/superpowers/specs/2026-08-06-openrouter-direct-analysis-design.md`

## Global Constraints

- No OpenAI SDK, LangChain, LlamaIndex, or vector DB.
- No real network in unit/CI tests.
- Never log `LLM_API_KEY`, Authorization header, full prompts, or source snippets.
- Missing `LLM_API_KEY` when `LLM_PROVIDER=openrouter` fails before any HTTP attempt.
- Do not silently fall back from OpenRouter failure to `FakeLLM`.
- Do not change Week 1–2 commands or `results/normalized/findings.json`.
- Commits only after user approval (see `.agents/rules/git_commit_workflow.md`).

---

### Task 1: OpenRouter config defaults and validation

**Files:**
- Modify: `week3/config.py`
- Modify: `tests/week3/test_config.py`
- Create: `.env.example`
- Modify: `.gitignore` (ensure `.env` ignored)

**Interfaces:**
- Consumes: `os.environ`
- Produces: `AppConfig` fields:
  - `provider_type: str` (`openrouter` | `fake`)
  - `base_url: str` default `https://openrouter.ai/api/v1`
  - `model_name: str` default `deepseek/deepseek-v4-flash-0731`
  - `api_key: str`
  - `timeout: float` from `LLM_TIMEOUT_SECONDS` (fallback `LLM_TIMEOUT` if present)
  - `max_retries: int` from `LLM_MAX_RETRIES` default `1`
  - `require_api_key_for_openrouter()` or equivalent validation used by callers

- [ ] **Step 1: Update failing config tests**

```python
def test_config_openrouter_defaults(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("LLM_TIMEOUT", raising=False)
    cfg = AppConfig.from_env()
    # Accept either keeping fake as code default OR openrouter as documented runtime default;
    # for this task set defaults: provider openrouter OR document that analyze CLI sets openrouter.
    # Required defaults below must hold when env unset:
    assert cfg.base_url == "https://openrouter.ai/api/v1"
    assert cfg.model_name == "deepseek/deepseek-v4-flash-0731"
    assert cfg.timeout == 60.0
    assert cfg.max_retries == 1


def test_config_from_env_openrouter(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("LLM_MODEL", "deepseek/deepseek-v4-flash-0731")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "45")
    monkeypatch.setenv("LLM_API_KEY", "sk-test-not-real")
    cfg = AppConfig.from_env()
    assert cfg.provider_type == "openrouter"
    assert cfg.timeout == 45.0
    assert cfg.api_key == "sk-test-not-real"
```

- [ ] **Step 2: Run tests to confirm current gaps**

Run: `python3 -m pytest -q tests/week3/test_config.py -v`
Expected: FAIL or outdated assertions on provider defaults (`openai` / `LLM_TIMEOUT` only).

- [ ] **Step 3: Implement config**

Update `week3/config.py`:

```python
provider_type: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openrouter"))
model_name: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "deepseek/deepseek-v4-flash-0731"))
api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"))
timeout: float = field(default_factory=lambda: float(
    os.getenv("LLM_TIMEOUT_SECONDS", os.getenv("LLM_TIMEOUT", "60"))
))
max_retries: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_RETRIES", "1")))
```

Add a small helper used by the OpenRouter caller:

```python
def ensure_openrouter_ready(self) -> None:
    if self.provider_type != "openrouter":
        return
    if not self.api_key.strip():
        raise ValueError("LLM_API_KEY is required when LLM_PROVIDER=openrouter")
    if not self.base_url.startswith("https://"):
        raise ValueError("LLM_BASE_URL must be an HTTPS URL")
```

- [ ] **Step 4: Add `.env.example` and ignore `.env`**

`.env.example`:

```dotenv
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=
LLM_MODEL=deepseek/deepseek-v4-flash-0731
LLM_TIMEOUT_SECONDS=60
LLM_MAX_RETRIES=1
```

Ensure `.gitignore` contains:

```gitignore
.env
```

- [ ] **Step 5: Re-run config tests**

Run: `python3 -m pytest -q tests/week3/test_config.py -v`
Expected: PASS

---

### Task 2: Direct OpenRouter HTTP client

**Files:**
- Create: `week3/llm/openrouter.py`
- Modify: `week3/llm/__init__.py` (export if useful)
- Create: `tests/week3/test_openrouter.py`
- Create if missing: `prompts/security_analysis_system.md` (content from implementation_plan §3.1)

**Interfaces:**
- Consumes: `AnalysisPacket`, `LLMResult` from `week3.llm.base`
- Produces:
  - `class OpenRouterClient:` with `analyze(self, packet: AnalysisPacket, system_prompt: str) -> LLMResult`
  - Or module function `call_openrouter(...)` returning `LLMResult`
  - Request URL: `{base_url.rstrip('/')}/chat/completions`
  - Parses first choice `message.content` as JSON object into `LLMResult.parsed_response`

- [ ] **Step 1: Write failing HTTP-boundary tests with mocked transport**

```python
import json
from unittest.mock import patch, MagicMock
from week3.llm.base import AnalysisPacket
from week3.llm.openrouter import OpenRouterClient


def _ok_body(content_obj):
    return json.dumps({
        "id": "gen-1",
        "model": "deepseek/deepseek-v4-flash-0731",
        "choices": [{"message": {"role": "assistant", "content": json.dumps(content_obj)}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }).encode("utf-8")


def test_openrouter_posts_expected_payload(monkeypatch):
    client = OpenRouterClient(
        api_key="sk-secret-key",
        base_url="https://openrouter.ai/api/v1",
        model="deepseek/deepseek-v4-flash-0731",
        timeout_seconds=5.0,
        max_retries=1,
    )
    packet = AnalysisPacket(group_key="g1", finding_group={"source_finding_ids": ["f1"]})
    captured = {}

    class Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return _ok_body({"schema_version": "1.0", "group_key": "g1"})
        status = 200

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.header_items()) if hasattr(req, "header_items") else {
            k: v for k, v in req.headers.items()
        }
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return Resp()

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = client.analyze(packet, system_prompt="SYS")
    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert captured["body"]["model"] == "deepseek/deepseek-v4-flash-0731"
    assert captured["body"]["temperature"] == 0
    assert captured["body"]["response_format"] == {"type": "json_object"}
    assert captured["body"]["messages"][0] == {"role": "system", "content": "SYS"}
    assert result.error is None
    assert result.parsed_response["group_key"] == "g1"
    # secret must not appear in result.error / str(result)
    assert "sk-secret-key" not in (result.error or "")


def test_missing_api_key_does_not_call_network():
    client = OpenRouterClient(api_key="", base_url="https://openrouter.ai/api/v1",
                              model="deepseek/deepseek-v4-flash-0731", timeout_seconds=5.0, max_retries=1)
    with patch("urllib.request.urlopen") as mocked:
        try:
            client.analyze(AnalysisPacket(group_key="g1"), system_prompt="SYS")
            assert False, "expected config error"
        except ValueError as e:
            assert "LLM_API_KEY" in str(e)
        mocked.assert_not_called()


def test_retries_once_on_http_500():
    # First urlopen raises/returns 500, second returns 200 — assert call_count == 2
    ...


def test_no_retry_on_http_400():
    # 400 once — assert call_count == 1 and error set without leaking body secrets
    ...
```

- [ ] **Step 2: Run tests — expect FAIL (module missing)**

Run: `python3 -m pytest -q tests/week3/test_openrouter.py -v`
Expected: FAIL import / missing `OpenRouterClient`

- [ ] **Step 3: Implement `week3/llm/openrouter.py`**

Minimal behavior:

1. Validate non-empty API key and HTTPS base URL.
2. Build JSON body as in design doc.
3. `urllib.request.Request` with headers `Authorization: Bearer ...`, `Content-Type: application/json`.
4. On success: parse `choices[0].message.content` as JSON object.
5. On malformed JSON / empty content / transport / 429 / 5xx: retry once if `max_retries >= 1`, then set `LLMResult.error`.
6. Never include API key in exception messages or `LLMResult.error`.
7. Map usage tokens into `LLMResult` when present.

- [ ] **Step 4: Ensure system prompt file exists**

If missing, create `prompts/security_analysis_system.md` using the English hard-rules block from `.agents/implementation_plan.md` §3.1. Load with `Path.read_text(encoding="utf-8")` at call site — do not hardcode the full prompt in Python.

- [ ] **Step 5: Re-run OpenRouter tests + FakeLLM tests**

Run:

```bash
python3 -m pytest -q tests/week3/test_openrouter.py tests/week3/test_fake_llm.py -v
python3 -m compileall -q week3
```

Expected: PASS

---

### Task 3: Wire selection into Week 3 analyze entrypoint + docs

**Files:**
- Create or modify analyze entrypoint as available: `week3/cli.py` and/or `week3/analyzer.py` (create minimal if not present yet)
- Modify: `README.md`
- Modify: `Makefile` only if `analyze` / `analyze-mock` targets are being added in this same change; otherwise document CLI only

**Interfaces:**
- Consumes: `AppConfig`, `OpenRouterClient`, `FakeLLM`
- Produces: provider selection:
  - `--provider fake` or `LLM_PROVIDER=fake` → `FakeLLM`
  - `LLM_PROVIDER=openrouter` (default for real runs) → `OpenRouterClient`
- If full pipeline (grouping/evidence) is not ready, expose a thin callable that accepts an `AnalysisPacket` and writes/returns `LLMResult` so OpenRouter path is usable and testable without inventing Week 4 features.

- [ ] **Step 1: Add a selection helper test**

```python
def test_provider_factory_openrouter(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    from week3.llm.factory import build_llm  # or wherever selection lives
    llm = build_llm(AppConfig.from_env())
    assert llm.__class__.__name__ == "OpenRouterClient"


def test_provider_factory_fake(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    from week3.llm.factory import build_llm
    llm = build_llm(AppConfig.from_env())
    assert llm.__class__.__name__ == "FakeLLM"
```

- [ ] **Step 2: Implement selection + README**

README additions (Vietnamese ok):

```markdown
## Week-3 — Security Analysis Agent (LLM)

1. Copy `.env.example` → `.env` and set `LLM_API_KEY` (do not commit `.env`).
2. Mock/offline: `LLM_PROVIDER=fake` or `--provider fake`.
3. Real OpenRouter run uses model `deepseek/deepseek-v4-flash-0731`.
4. Tests: `python3 -m pytest -q tests/week3` (no network).
```

- [ ] **Step 3: Full offline verification**

```bash
python3 -m pytest -q tests/week3
python3 -m compileall -q week3
make normalize
make search Q='SQL Injection'
```

Expected: all PASS / exit 0.

- [ ] **Step 4: Prepare Round 2 handoff (do not commit unless user asks)**

Produce:

```text
## Handoff — Round 1 complete
### Changed files
<git diff --stat>
### Acceptance criteria
- [ ] OpenRouter direct HTTPS path implemented
- [ ] FakeLLM retained; tests offline
- [ ] Missing API key fails before network
- [ ] Retry policy covered by mocked tests
- [ ] .env.example present; .env ignored
### Commands run
| Command | Exit code |
```

---

## Spec coverage checklist

| Spec requirement | Task |
|---|---|
| POST OpenRouter chat/completions | Task 2 |
| Env vars + defaults | Task 1 |
| System prompt + packet JSON | Task 2–3 |
| Parse JSON → validation path | Task 2–3 |
| Retry once timeout/5xx/malformed | Task 2 |
| No secret logging | Task 2 |
| Keep FakeLLM | Task 2–3 |
| `.env.example` + README | Task 1 + 3 |
| No SDK / no CI real calls | Global + all tasks |

## Out of scope reminders

- Do not implement full evidence/grouping/retrieval if not already present — only what is needed to call OpenRouter with a packet and keep FakeLLM tests green.
- Do not weaken provenance/schema validators to accept bad model output.
- Do not commit `.env` or API keys.
