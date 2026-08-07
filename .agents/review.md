# Code Review Instructions & Guidelines (`.agents/review.md`)

This document defines the review checklist, severity scale, and escalation procedures for code changes in Project Sentinel.

---

## 1. Diff Review Checklist

When reviewing pull requests or git diffs, verify:

1. **Scope & Correctness**: Does the change accomplish its goal without introducing unintended side effects or breaking contracts?
2. **Path & Import References**: Are all imports pointing to `src/project_sentinel/`? Are legacy `week2/` or `week3/` paths avoided?
3. **Validation & Handling**: Is input validated? Are errors handled gracefully with correct CLI exit codes?
4. **Security & Secrets**: Are secrets, API keys, or raw tokens kept out of code and logs? Is WebGoat binding strictly loopback?
5. **Testing**: Are fast, deterministic unit tests included for new features or bug fixes?
6. **Report Invariance**: Are historical sprint reports under `reports/` left untouched?

---

## 2. Severity Scale

| Severity | Definition | Review Action |
| --- | --- | --- |
| **Critical** | Exploitable vulnerability, auth bypass, secret leak, or data destruction | Immediate block; escalation required |
| **High** | Real correctness/security bug in plausible execution paths | Must fix before merge |
| **Medium** | Missing validation, weak error handling, or test gap | Recommended fix before release |
| **Low** | Code style, minor formatting, or unnecessary complexity | Discretionary fix |
| **Info** | Informational note or suggestion | Non-blocking |

---

## 3. Escalation Conditions (Round 3 Deep Pass)

Escalate to a Deep Review pass if any of the following triggers occur:
1. Diff touches authentication, secrets, or credential handling.
2. Diff modifies Docker infrastructure, CI workflows, or execution boundaries.
3. Unconfirmed High or Critical severity findings exist.
4. Concurrency, state mutation, or security schema changes are made.
