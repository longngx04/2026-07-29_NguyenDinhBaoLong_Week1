# Multi-Agent Workflow

Three-round pipeline for this repository. Each round has a fixed agent and scope.
**Cursor self-selects the review model** based on diff complexity — see [`rules/model_selection.md`](rules/model_selection.md).

Do not skip rounds or merge roles unless the user explicitly overrides.

## Model Configuration

| Agent | Round | Model | When to use |
| --- | --- | --- | --- |
| Antigravity | 1 — Implement | **Gemini 3.6 Flash** | Always for coding tasks |
| Cursor | 2 — Review | **Auto-select** (see below) | Every implementation handoff |
| Cursor | 3 — Escalate | **Claude Sonnet 5 Thinking** | When mid-review upgrade or Deep findings need confirmation |

### Cursor review model — auto-select by complexity

Cursor **must assess the diff and pick a model before reviewing**. Do not default blindly to one model.

| Complexity | Model | Typical diff |
| --- | --- | --- |
| **Light** | GPT-5.6 Luna | Docs, config, ≤2 files / ≤50 lines, no security surface |
| **Standard** | Composer 2.5 Standard | Routine code in one module, ≤5 files / ≤300 lines |
| **Deep** | Claude Sonnet 5 Thinking | Auth/secrets, shell/Docker/CI, injection, multi-module, large diffs |

Full decision rules: [`rules/model_selection.md`](rules/model_selection.md)

### Model settings (defaults)

- Do **not** enable Fast, Max Context, or Thinking by default (except Thinking is inherent to Sonnet 5 Thinking tier).
- Do **not** use Opus for routine work.
- Prefer **small, targeted context** (git diff or changed-file list) over re-reading the full repository.

## Round 1 — Antigravity implements

**Agent**: Antigravity · **Model**: Gemini 3.6 Flash · **Rule**: [`rules/role_coder.md`](rules/role_coder.md)

1. Read `context.md`, `implementation_plan.md`, and all files in `.agents/`.
2. Implement in **small, incremental tasks** — one logical unit per commit when possible.
3. Run tests, lint, and static analysis before handoff.
4. Produce a **git diff** (or explicit changed-file list) as the handoff artifact.
5. Self-check against the acceptance criteria in `implementation_plan.md`.

**Handoff to Round 2 must include:**

```
git diff                    # or git diff --stat + git diff <paths>
Changed files: <list>       # if diff is too large, list paths only
Acceptance criteria status: pass | partial | fail (with notes)
Commands run: <test/lint/static-analysis commands + exit codes>
```

## Round 2 — Cursor reviews (diff-only, auto-model)

**Agent**: Cursor · **Model**: auto-selected · **Rules**: [`rules/role_reviewer.md`](rules/role_reviewer.md) + [`rules/model_selection.md`](rules/model_selection.md)

### Step 0 — Select model (before reading code)

1. Run or read `git diff --stat` to gauge size and files touched.
2. Apply complexity signals from [`rules/model_selection.md`](rules/model_selection.md).
3. Output `MODEL SELECTED` and `COMPLEXITY` lines before findings.

### Input scope — critical for token efficiency

Review **only** the supplied git diff or changed-file list plus directly related call paths.
Do **not** re-read the entire repository unless the user explicitly requests it.

### Review focus

- Correctness and unintended behavior changes
- Missing input validation and error handling
- Security issues and permission bypasses
- Missing or weak tests
- Unnecessary complexity
- Violations of repository rules (`.agents/`, `README.md`, `Makefile`, CI)

### Constraints

- **Do not rewrite the code.** Report findings only; Antigravity applies fixes in a new Round 1 pass.
- Ignore formatting issues already covered by linters.
- Only report **actionable** findings with clear evidence.
- Every finding must cite `File:Line` from the diff.

### Required output — findings table

| Severity | File:Line | Issue | Why it matters | Recommended fix |
| --- | --- | --- | --- | --- |
| … | … | … | … | … |

If no actionable issues: return the table with a single row `— | — | No actionable findings | — | —`.

### Mid-review upgrade → Round 3

If Round 2 started on Light or Standard and a deeper pass is needed, upgrade to Deep and re-review.
See Round 3 triggers below.

## Round 3 — Escalate (conditional, Deep review)

**Agent**: Cursor · **Model**: Claude Sonnet 5 Thinking
**Rule**: [`rules/role_reviewer_escalation.md`](rules/role_reviewer_escalation.md)

### Triggers — enter Round 3 when **any** of these is true

1. Round 2 started on Light/Standard and issued `MODEL UPGRADE → Deep` mid-review.
2. Round 2 (any model) reports **High** or **Critical** severity and findings need confirmation.
3. Code touches **authentication, authorization, or secrets** but Round 2 ran on Light/Standard.
4. Change spans **multiple modules with complex dependencies** assessed on a lower tier.
5. Tests pass but **runtime behavior is still suspicious**.
6. Round 2 (lower tier) and Round 1 (Antigravity) reach **contradictory conclusions**.

If Round 2 already ran on **Deep** and produced confirmed findings, **skip Round 3** — deliver Round 2 output directly.

### Input scope

Same as Round 2: supplied diff + directly related call paths only.
Verify each suspected issue against the actual code before reporting.

### Priority order

1. Authentication and authorization bypass
2. Trust-boundary violations
3. Injection and unsafe data flows
4. Insecure defaults
5. Business-logic vulnerabilities
6. Concurrency and state inconsistencies
7. Missing negative tests

### Required output — three sections

**Confirmed defects** — verified issues with evidence and targeted fix.

**Risks requiring runtime verification** — plausible but unconfirmed; include debug command,
expected vs. actual, and hypothesis.

**Non-issues / false positives** — items from Round 2 that do not hold up under deeper review.

Do not suggest broad refactoring unless required to fix a confirmed defect.

## Loop after review

```
Round 1 (Antigravity) → Round 2 (Cursor: auto-select model, diff review)
                              ↓
              Upgrade needed or High/Critical unconfirmed?
                     /              \
                   yes               no
                    ↓                 ↓
            Round 3 (Deep/Sonnet)   Apply Round 2 fixes
                    ↓                 ↓
            Merge findings ←──────────┘
                    ↓
            Round 1 (Antigravity fixes)
                    ↓
            Round 2 (re-review diff, re-assess model tier)
                    ↓
            Repeat until APPROVE or user accepts
```

## Severity scale (shared across rounds)

| Severity | Meaning | Round 3 required? |
| --- | --- | --- |
| **Critical** | Exploitable security hole, auth bypass, secret leak, data loss | Yes (if not already on Deep) |
| **High** | Real bug with security or correctness impact in plausible cases | Yes (if not already on Deep) |
| **Medium** | Missing validation, weak error handling, test gap | No (unless auth/secrets involved) |
| **Low** | Maintainability, unnecessary complexity | No |
| **Info** | Observation, not blocking | No |
