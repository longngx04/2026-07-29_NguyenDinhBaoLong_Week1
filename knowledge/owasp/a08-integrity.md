---
title: OWASP A08 Software and Data Integrity Failures
tags: [owasp, a08, integrity, deserialization, supply-chain]
---

# OWASP A08:2021 — Software and Data Integrity Failures

Failures related to code and infrastructure that does not protect integrity. Unsafe deserialization of untrusted data is a common example.

## Why it matters

Deserializing attacker-controlled bytes can lead to remote code execution or logic bypass.

## Safe patterns

- Prefer safe formats (JSON with schema validation) over Java native serialization.
- Never deserialize untrusted `ObjectInputStream` data without a strict allowlist.
- Verify signatures for updates and critical artifacts.

## Related in this project

OpenGrep may flag `ObjectInputStream.readObject` usage.
