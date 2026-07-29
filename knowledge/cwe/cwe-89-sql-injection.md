---
title: CWE-89 SQL Injection
tags: [cwe-89, cwe, sql-injection, injection]
---

# CWE-89 — SQL Injection

The software constructs SQL using externally influenced input without neutralizing special elements.

## Detection hints

String concatenation or formatting into `Statement.execute`, `executeQuery`, or `executeUpdate`.

## Mitigation

Use parameterized `PreparedStatement` APIs; never concatenate user input into SQL text.
