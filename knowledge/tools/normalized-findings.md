---
title: Reading normalized findings
tags: [tool, normalized, findings, sentinel]
---

# Reading normalized findings

After `make normalize`:

- `results/normalized/findings.json` — JSON array for humans and simple tools
- `results/normalized/findings.jsonl` — one finding per line for agents/pipelines

Fields include `tool`, `severity`, `file_or_url`, `title`, `cwe`, `owasp`, and `message`.
