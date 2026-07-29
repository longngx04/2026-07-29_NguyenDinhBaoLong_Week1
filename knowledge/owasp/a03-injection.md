---
title: OWASP A03 Injection
tags: [owasp, a03, injection, sql-injection, command-injection]
---

# OWASP A03:2021 — Injection

Injection flaws happen when untrusted data is sent to an interpreter as part of a command or query. Classic forms include SQL injection, OS command injection, and LDAP injection.

## Why it matters

Attackers can read or change data, take over accounts, or run system commands depending on the sink.

## Safe patterns

- Prefer parameterized queries / prepared statements for SQL.
- Avoid building shell commands from user input; use allowlists and safe APIs.
- Validate and encode input at trust boundaries.

## Related in this project

OpenGrep rules may flag `Statement.execute*` (SQL) and `Runtime.exec` (command injection).
