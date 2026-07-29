---
title: OWASP A01 Broken Access Control
tags: [owasp, a01, access-control, authorization]
---

# OWASP A01:2021 — Broken Access Control

Users can act outside their intended permissions. Examples include IDOR, missing function-level checks, and forced browsing.

## Safe patterns

- Deny by default; check authorization on every request.
- Enforce ownership checks on object IDs.
- Log access-control failures.
