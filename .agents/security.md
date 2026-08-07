# Security Guidelines & Invariants (`.agents/security.md`)

This document details the security constraints, boundaries, and guardrails for Project Sentinel.

---

## 1. Security Invariants

1. **Secret Isolation**:
   - Never commit `.env` or hardcode API keys, tokens, or credentials.
   - Do not print `Authorization` headers, API keys, or full prompts containing secrets in application logs.
   - `.env.example` must contain only empty or placeholder values.

2. **Offline Test Boundary**:
   - `pytest` unit tests must execute completely offline using `FakeLLM`.
   - Never initiate real HTTP requests to external LLM providers during automated CI test runs.

3. **Vulnerable Target Isolation**:
   - OWASP WebGoat is a intentionally vulnerable application.
   - In `docker-compose.yml`, WebGoat ports **must only bind to loopback `127.0.0.1`** (`127.0.0.1:8080:8080`).
   - Never bind WebGoat to `0.0.0.0` or expose it to public interfaces.

4. **Provenance & Anti-Hallucination Guardrails**:
   - The Security Analysis Agent MUST NOT invent line numbers, file paths, CWEs, OWASP tags, or finding IDs.
   - All output records are validated against `schemas/security-analysis-record.schema.json` and strict provenance validators (`validate_provenance`).
   - Never remove or weaken schema/provenance checks to make a test pass.

5. **No Exploit Generation**:
   - The agent acts purely as an analytical security triage component.
   - Exploit payloads, attack vectors, or destructive execution instructions must never be generated.
