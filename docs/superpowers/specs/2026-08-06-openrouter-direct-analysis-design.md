# OpenRouter Direct Analysis Design

## Goal

Enable the Week 3 security-analysis runtime to call OpenRouter's OpenAI-compatible Chat Completions API with:

```text
model: deepseek/deepseek-v4-flash-0731
base URL: https://openrouter.ai/api/v1
```

The real provider is for manual/local analysis runs only. Unit tests and CI remain offline and deterministic through the existing `FakeLLM`.

## Scope

### In scope

- Make an authenticated HTTPS `POST` to:
  `https://openrouter.ai/api/v1/chat/completions`.
- Read these environment variables:

  ```dotenv
  LLM_PROVIDER=openrouter
  LLM_BASE_URL=https://openrouter.ai/api/v1
  LLM_API_KEY=
  LLM_MODEL=deepseek/deepseek-v4-flash-0731
  LLM_TIMEOUT_SECONDS=60
  LLM_MAX_RETRIES=1
  ```

- Build a Chat Completions request using the version-controlled system prompt and the bounded `AnalysisPacket` JSON as the user message.
- Extract the assistant message content, parse it as one JSON object, and send it to the existing schema and provenance validation path.
- Retry at most once for timeouts, transient transport failures, HTTP 5xx responses, and malformed model JSON.
- Produce concise errors without exposing the API key, authorization header, complete prompt, or source snippets in logs.
- Retain `FakeLLM` for tests and CI. It must not make network calls.
- Document local setup and a real-provider run command without committing secrets.

### Out of scope

- Do not add LangChain, LlamaIndex, a vector database, or an OpenAI SDK.
- Do not call OpenRouter in test or CI.
- Do not give the model browser, shell, filesystem-write, or tool access.
- Do not create a fallback that silently changes a failed OpenRouter run into fake analysis.
- Do not change Week 1–2 commands or normalized findings.

## Architecture

The production path calls OpenRouter directly from the Week 3 analysis pipeline instead of routing the request through the generic provider abstraction.

```text
validated finding group
  -> deterministic evidence/retrieval packet
  -> system prompt + JSON packet
  -> direct HTTPS request to OpenRouter
  -> assistant JSON content
  -> JSON parsing
  -> schema + provenance validation
  -> JSONL record
```

`FakeLLM` stays available solely to the mock execution and test paths. It is not deleted because it provides the required offline test boundary.

## Request Contract

### Preconditions

When `LLM_PROVIDER=openrouter`:

1. `LLM_API_KEY` must be non-empty. Otherwise stop before any network request with a configuration error.
2. `LLM_BASE_URL` must be an HTTPS URL and default to `https://openrouter.ai/api/v1`.
3. `LLM_MODEL` defaults to `deepseek/deepseek-v4-flash-0731`.
4. `LLM_TIMEOUT_SECONDS` and `LLM_MAX_RETRIES` must parse to bounded positive values.

### HTTP request

Use Python standard-library HTTPS facilities. Send:

```json
{
  "model": "deepseek/deepseek-v4-flash-0731",
  "messages": [
    {"role": "system", "content": "<system prompt>"},
    {"role": "user", "content": "<serialized AnalysisPacket>"}
  ],
  "temperature": 0,
  "response_format": {"type": "json_object"}
}
```

Set `Authorization: Bearer <LLM_API_KEY>` and `Content-Type: application/json`.

The implementation must use the response's first choice message content only. Missing choices/content, non-object JSON, and provider error envelopes are failures; they must never become a fabricated report.

## Failure and Retry Contract

| Case | Behavior | Retry |
| --- | --- | --- |
| Missing/invalid config | Clear config error; no HTTP request | No |
| DNS/TLS/timeout/connection reset | Provider failure | Yes, once |
| HTTP 429 or 5xx | Provider failure | Yes, once |
| Other HTTP 4xx | Clear provider error with status only; no secret/body dump | No |
| Empty choice/content or invalid JSON | Invalid model-output error | Yes, once |
| Schema/provenance rejection | Existing validator failure flow | At most one corrective retry if the pipeline already supports it |
| Retry exhausted | Fail the group/run explicitly; do not write partial fabricated JSONL | No |

The retry implementation should be bounded and use a short deterministic or capped backoff. It must not retry indefinitely.

## Files Antigravity Should Change

| File | Required change |
| --- | --- |
| `week3/config.py` | Validate and expose the OpenRouter settings. Preserve fake mode for tests. Prefer `LLM_TIMEOUT_SECONDS`, while supporting the existing `LLM_TIMEOUT` only if backward compatibility is needed. |
| Week 3 analysis/CLI module | Add the direct OpenRouter request path when `LLM_PROVIDER=openrouter`; preserve an explicit fake path for offline execution. |
| `prompts/security_analysis_system.md` | Add only if absent; load it at runtime rather than embedding prompt text in Python. |
| `.env.example` | Add non-secret OpenRouter defaults and an empty `LLM_API_KEY=`. |
| `README.md` | Document `.env` setup, local real run, mock run, and that `.env` must not be committed. |
| `tests/week3/` | Add config and HTTP-boundary tests with mocked standard-library transport. Assert no real network is used and no secret appears in errors. |

Antigravity may add a small focused helper module for the HTTP boundary if the pipeline is not yet present. It must not introduce a new generic provider abstraction, external SDK, or framework.

## Acceptance Criteria

1. With `LLM_PROVIDER=openrouter`, a valid API key, and mocked HTTP transport, the pipeline sends the expected endpoint, model, authorization header, system prompt, and serialized packet.
2. A successful provider response whose message content is JSON reaches existing output validation.
3. Missing `LLM_API_KEY` fails before transport is invoked.
4. Timeouts and HTTP 5xx retry no more than once; non-retryable 4xx does not retry.
5. Invalid provider JSON fails clearly after the configured retry limit.
6. Error messages and logs never include the API key or authorization header.
7. `FakeLLM` tests still pass with no network access.
8. Existing Week 2 commands (`make normalize`, `make search`) remain unaffected.

## Verification Commands

```bash
python3 -m pytest -q tests/week3
python3 -m compileall -q week3
make normalize
make search Q='SQL Injection'
```

After the offline checks pass, a user may perform a manual real-provider smoke test with a local `.env` containing `LLM_API_KEY`. This command must not be placed in CI and no token may be printed or committed.

## Risks and Rollback

- Real calls incur cost and depend on OpenRouter availability. The mock path keeps CI reproducible.
- Model output remains untrusted; schema/provenance validation is mandatory before JSONL output.
- If the real path misbehaves, set `LLM_PROVIDER=fake` for local mock runs and remove only the new direct-call path in a follow-up change. Do not weaken validators to accommodate provider output.
