---
title: Normalized findings schema
tags: [schema, findings, agent, normalize]
---

# Normalized findings schema

Mỗi cảnh báo sau `week2.normalize` có các field chính:

- `tool` — ví dụ `opengrep`
- `severity` — `high` / `medium` / `low` / `info`
- `file_or_url` — đường dẫn source hoặc URL
- `title` — mô tả ngắn
- `message` — mô tả đầy đủ từ tool
- `rule_id`, `cwe`, `owasp`, `line`, `fingerprint`

File tổng hợp: `results/normalized/findings.json` (`count` + mảng `findings`).
