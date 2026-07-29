---
title: OpenGrep in Project Sentinel
tags: [opengrep, tool, sast, sentinel]
---

# OpenGrep in Project Sentinel

Week-1 runs OpenGrep `v1.26.0` with rules in `rules/opengrep/java-security.yml`.

Native output: `results/raw/opengrep.json` with `results[]` and `errors[]`.

Week-2 normalize maps each result to a shared finding schema in `results/normalized/`. Severity `ERROR` becomes `high`. Rule ids keep the short name (for example `java-sql-statement-execution`).
