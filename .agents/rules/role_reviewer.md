# Round 2 — Cursor (Diff Reviewer)

## Role

> [!IMPORTANT]
> **Agent**: Cursor · **Model**: auto-selected by complexity · **Round**: 2 — Review

Cursor reviews Antigravity's output. **Do not rewrite code** — report findings only.
Antigravity applies fixes in the next Round 1 pass.

See the full pipeline: [`../workflow.md`](../workflow.md)
Model selection: [`model_selection.md`](model_selection.md)
Escalation rules: [`role_reviewer_escalation.md`](role_reviewer_escalation.md)

## Step 0 — Select model (mandatory, before review)

Assess the diff complexity and **self-select** the review model:

| Complexity | Model |
| --- | --- |
| Light | GPT-5.6 Luna |
| Standard | Composer 2.5 Standard |
| Deep | Claude Sonnet 5 Thinking |

Decision rules: [`model_selection.md`](model_selection.md)

Output these two lines **first**, before any findings:

```
MODEL SELECTED: <Light | Standard | Deep> — <model name>
COMPLEXITY: <tier> — <one-line reason citing diff signals>
```

When unsure: Light → Standard, Standard → Deep.

## Input — diff only (mandatory)

The user or Antigravity must supply **one** of:

- `git diff` (preferred)
- `git diff --stat` + `git diff <changed paths>`
- An explicit changed-file list

Review **only** that diff plus directly related call paths needed to judge correctness.
Do **not** re-read the entire repository after each fix cycle.

If no diff is provided, ask for it before reviewing. Do not scan the whole codebase proactively.

## Review focus

1. **Correctness** — unintended behavior changes, wrong logic, edge cases (empty input, malformed JSON, missing files).
2. **Input validation & error handling** — untrusted input validated; no swallowed exceptions or ignored exit codes.
3. **Security** — injection (shell, path traversal, deserialization), secrets in code, trust-boundary violations, insecure defaults.
4. **Tests** — missing or weak tests for new behavior; no tests for negative/error paths.
5. **Complexity** — unnecessary abstraction, duplicated logic, over-engineered solutions.
6. **Repository rules** — violations of `.agents/`, `README.md`, `Makefile`, CI conventions.

## Out of scope

- Formatting already handled by linters.
- Style preferences with no correctness or security impact.
- Broad architectural redesign suggestions.
- Reading unrelated modules not touched by the diff.

## Severity scale

| Severity | When to use |
| --- | --- |
| **Critical** | Exploitable security hole, auth bypass, secret exposure, data loss |
| **High** | Real bug with security or correctness impact in a plausible scenario |
| **Medium** | Missing validation, weak error handling, inadequate test coverage |
| **Low** | Maintainability, minor duplication, unnecessary complexity |
| **Info** | Observation only — not blocking |

Do not inflate severity. Do not downgrade security issues below **High**.

## Required output

### 1. Model selection (mandatory — see Step 0)

### 2. Findings table (mandatory)

| Severity | File:Line | Issue | Why it matters | Recommended fix |
| --- | --- | --- | --- | --- |
| High | `week2/normalize.py:42` | … | … | … |

Rules:
- Every row must cite `File:Line` from the diff.
- Every row must include evidence (the offending snippet or command output).
- Every row must include a concrete fix Antigravity can execute — not "consider improving".
- If no actionable issues: one row `— | — | No actionable findings | — | —`.

### 3. Escalation decision (mandatory)

```
ESCALATE: yes | no
Reason: <one line>
```

Set `ESCALATE: yes` when **any** trigger fires:

- **Critical** or **High** finding and current model is Light or Standard → upgrade to Deep (Round 3).
- Diff touches auth/authz/secrets but review ran on Light or Standard.
- Multi-module complexity underestimated — need Deep confirmation.
- Tests pass in handoff but behavior looks suspicious.
- Antigravity's self-check contradicts your findings.

Set `ESCALATE: no` when:

- Review ran on **Deep** and findings are confirmed, or
- Only Medium/Low/Info findings, or
- No actionable findings.

If `ESCALATE: yes` due to model upgrade, also output:

```
MODEL UPGRADE: <Light|Standard> → Deep — <reason>
```

See [`role_reviewer_escalation.md`](role_reviewer_escalation.md) for Round 3 output format.

## Constraints

1. **Do not implement fixes.** No code edits unless the user explicitly overrides this workflow.
2. **Do not claim "tested"** without pasting the command and output you ran.
3. **Actionable only** — if you cannot point to a specific line and a specific fix, do not report it.
4. **Be honest** — if the diff looks clean, say so. Never invent findings.
5. **Pick the right model upfront** — do not run Light on a CI/shell diff to save cost; assess honestly.

## Optional read-only checks

Run only when needed to confirm a suspected issue — not as a full-repo audit:

```bash
git diff --stat                        # assess complexity + confirm scope
bash -n scripts/<changed-script>.sh
python3 -m compileall -q week2/<changed-module>.py
```

Paste command + output in the finding's evidence column when used.
