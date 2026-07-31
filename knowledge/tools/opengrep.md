---
title: OpenGrep scanner notes
tags: [opengrep, semgrep, sast, tool, java, pattern]
---

# OpenGrep — tool notes

OpenGrep là CLI SAST kiểu pattern-matching (họ Semgrep). Project Sentinel Week-1 pin bản `v1.26.0`, quét Java WebGoat bằng rule trong `rules/opengrep/`.

## Output gốc

File `results/raw/opengrep.json` có:

- `version` — phiên bản CLI
- `results[]` — từng finding (`check_id`, `path`, `start.line`, `extra.message`, `extra.severity`, `extra.metadata`)
- `errors[]` — lỗi engine (Week-1 chạy sạch: `[]`)

Severity tool: `ERROR` / `WARNING` / `INFO`. Week-2 map sang `high` / `medium` / `low`.

## Rule đang dùng

| Rule id | CWE | Ý nghĩa |
| --- | --- | --- |
| `java-sql-statement-execution` | CWE-89 | SQL Injection pattern |
| `java-unsafe-deserialization` | CWE-502 | Insecure deserialization |
| `java-command-execution` | CWE-78 | OS command injection |

## Chuẩn hóa

`python -m week2.normalize` đọc JSON gốc và ghi `results/normalized/findings.json` với schema chung (`tool`, `severity`, `file_or_url`, `title`, …) để Agent dễ dùng.
