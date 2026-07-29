---
title: CWE-78 OS Command Injection
tags: [cwe-78, cwe, command-injection, injection]
---

# CWE-78 — OS Command Injection

The product builds an OS command using externally influenced input without neutralizing special elements.

## Detection hints

`Runtime.exec`, `ProcessBuilder` with unsanitized strings, shell wrappers.

## Mitigation

Avoid shells; pass fixed argument arrays; allowlist commands and arguments.
