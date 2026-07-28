# Stage 01 — Research (inspect first)

Rule: INSPECT what already exists. Evidence required — links, quotes, screenshots.
"I think there's nothing like this" without searching = gate fail.

> Project type (`/flow project-type`, default `web`): items 2 and 4 below are written for a
> **web / market-facing product**. For an **internal tool / cli / library / skill** (no public
> market), use the non-web framing in each item — it is still real evidence (first-party
> friction, who-benefits), NOT an excuse to skip. The semantic gate refuses a market product
> that hides behind the soft framing.

## Gate — check ALL before `/flow next`
- [x] I actually OPENED 3 existing tools/competitors (links below, with one honest note each)
- [x] **(web)** I found 3 REAL user complaints online, quoted, with source links — **OR (non-web/internal)** I named the concrete first-party friction / observed pain that justifies this
- [x] I wrote what competitors CHARGE (real prices) and who pays — **OR (non-web)** what people spend AROUND this problem today (time, a worse tool, manual work)
- [x] **(web)** I named the ONE channel my first 10 users come from (a place, not "social media") — **OR (non-web/internal)** I named who benefits and how they hear about it (release notes / team), and noted "no market channel" is NOT a kill signal for an internal tool
- [x] I wrote why those users would pick this over the status quo (one honest paragraph)
- [x] I wrote what is technically free vs hard for this idea
- [x] No FILL placeholders remain in this file

## What exists already (3 — open them, don't guess)

1. [OWASP WebGoat](https://github.com/WebGoat/WebGoat) — target Java/Spring application intentionally containing security lessons; its release includes a Docker image, but it is not itself a repeatable multi-tool scan pipeline.
2. [OpenGrep](https://github.com/opengrep/opengrep) — rule-based SAST engine compatible with Semgrep rules and able to emit JSON/SARIF; it needs a pinned local rule set to make findings reproducible.
3. [OWASP Find Security Bugs](https://find-sec-bugs.github.io/) — SpotBugs plugin for Java security audits; it analyzes compiled bytecode and emits SARIF/XML rather than OpenGrep's source-rule JSON.

## What users say (web: 3 real complaints quoted+linked · non-web: real first-party friction)

1. > In the Week-1 kickoff exchange (2026-07-28), mentor Dương Mạnh Kiên asked the team to run SAST/DAST and produce the tools' output; this makes repeatable, inspectable output an explicit observed need for the VinUni × VinSOC intern team.
2. > In the same exchange, the mentor required a baseline that is as static/deterministic as possible; a single scanner result cannot answer that comparison need.
3. > The operator restarting Project Sentinel from Week 1 asked for a stepwise setup and supplied the six-week delivery brief; the current workspace had no Git repository, target, scanner, CI, or run result before this work began.

## GTM & business reality

Building is the cheap part now. Distribution and willingness-to-pay are where ideas die —
research them BEFORE planning, not after shipping.

### Who pays today, and how much (pricing reference points)

- WebGoat → free OWASP training target ([repository](https://github.com/WebGoat/WebGoat)); the team pays in local Docker/CI compute and safe environment setup.
- OpenGrep → LGPL-2.1 open-source engine ([repository](https://github.com/opengrep/opengrep)); the team pays in maintaining a pinned rule pack and reviewing findings.
- FindSecBugs → Apache-2.0 open-source Java security plugin ([repository](https://github.com/find-sec-bugs/find-sec-bugs)); the team pays in Maven compilation, memory/runtime, and comparing bytecode findings against ground truth in a later week.

### The first-10-users channel (web) · who-benefits (non-web/internal)

This is an internal teaching/delivery tool, not a market product. The primary beneficiaries are the VinUni × VinSOC Project Sentinel team and mentor Dương Mạnh Kiên; they learn about and use it through this repository's README, GitHub Actions run, and the scheduled Week-1 output check. No market channel is required or claimed.

### Why switch (vs the status quo)

The team will switch from ad-hoc local commands and screenshots to this pipeline because a single checked-in command will pin the WebGoat source/runtime and scanner versions, retain raw JSON/SARIF artifacts, and run the same checks in CI. It deliberately does not claim better detection than either upstream tool; its value is a repeatable experiment that makes the two tools' output reviewable and ready for Week 2 normalization.

## Technically free vs hard

- Free (solved by libraries/platforms): Docker Compose lifecycle, GitHub Actions artifact retention, OpenGrep JSON output, WebGoat's official Docker image, and FindSecBugs' packaged detector.
- Hard (custom work, real risk): pinning compatible source/runtime/tool versions, compiling WebGoat bytecode for FindSecBugs, defining a local OpenGrep rule set without silently changing coverage, and later mapping findings to WebGoat lesson ground truth without overstating precision or recall.
