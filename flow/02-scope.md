# Stage 02 — Scope (go/no-go)

Scope = features chosen by IMPACT × COST, inside your time budget.
KILL here is cheap and smart. Killing a weak idea at this gate is a SUCCESS outcome.

## Impact rubric (business value — score BEFORE looking at cost)

| Impact | Meaning |
|---|---|
| H | moves money or the core promise: gets users in (acquisition), gets them paying (revenue), or delivers the one job they came for |
| M | keeps users / saves real time weekly (retention, operations) |
| L | nice-to-have; nobody would pay for or switch over it |

Decision matrix: **H-impact features justify B/C cost** (via the C-paths below).
**L-impact features must be grade A or they're cut** — and even grade-A L-features are
cut when the budget is tight. The classic failure is a v1 full of A-grade L-impact
features: cheap to build, worthless to sell.

## AI coding grade rubric

| Grade | Meaning | Examples |
|---|---|---|
| A | cheap for AI | CRUD, forms, dashboards, content sites, API wrappers |
| B | moderate | file processing, 3rd-party integrations, auth via library, single LLM call, HITL AI drafts |
| C | expensive | realtime, payments from scratch, custom auth, autonomous agentic AI pipelines, heavy concurrency |

**Grade is a COST estimate, not a permission.** The gate is fit(grades, budget), not "no C allowed."
When a C feature is the real need, three honest paths:
1. **The C feature IS the product** → invert the cut: C goes FIRST (riskiest assumption first),
   everything else is minimized to serve it, and the budget is renegotiated against reality.
   But: one C proves the value prop — its siblings are v2 cards, not v1 scope.
2. **Re-architect C down to B** (highest-leverage move): multi-step agent → single LLM call;
   auto-send → human-approves-draft; custom pipeline → managed service / library.
   Same user value, one grade cheaper.
3. **Irreducible C that doesn't fit the budget** → KILL or re-budget. Both are honest.

## Gate — check ALL before `/flow next`
- [x] Every feature below has an IMPACT (H/M/L with the business reason) AND a grade (A/B/C)
- [x] No L-impact feature above grade A survives in v1
- [x] The suggested-features section was actually considered (each suggestion has an in/out decision)
- [x] fit(grades, budget) holds — every C in scope is justified as path 1, 2, or 3 above (written next to the feature)
- [x] If the product IS a C feature: it is FIRST in build order, and its sibling C features are on the cut list
- [x] The cut list is written (what I am NOT building in v1)
- [x] GO / KILL decision is written below
- [x] No FILL placeholders remain in this file

## Time budget

One Week-1 delivery window; the first demo must show WebGoat running, both SAST tools producing retained raw output, and a fresh-clone command that reproduces it.

## Features in v1 (each with impact AND grade)

- Pin WebGoat source as Git submodule at `v2025.3` and run the matching official Docker image via Docker Compose — impact H (the core job is a stable, authorized target) — grade A (standard Git/Docker configuration).
- Provide a curated, version-controlled OpenGrep Java security rule pack and a command that writes `opengrep.json` — impact H (the core Week-1 SAST evidence) — grade B (rule design and scan-exit handling require deliberate configuration).
- Build WebGoat bytecode and run FindSecBugs `1.14.0` as the deterministic comparison baseline, preserving SARIF/XML output — impact H (mentor-required baseline and evidence) — grade B (Java build/plugin execution and artifact paths).
- Run both scans in GitHub Actions and retain their raw output as workflow artifacts — impact H (any team member must be able to reproduce the evidence) — grade B (CI, caches, exit-code policy, and artifacts).
- Document architecture, safe local startup, scan commands, output schema locations, and discovered endpoints — impact M (reduces repeated setup/review time for the team) — grade A (documentation from verified commands).

## Suggested features (impact-first — proposed, not decided)

Up to 3 features NOT in the original idea, each chosen for business impact (how does this
get users in / get money in / keep users?). Grounded in the stage-01 GTM findings — e.g.
the first-10-users channel often implies a share/invite/referral surface; the pricing
research often implies an upsell or a paid tier. Default is OUT; each needs an explicit
decision.

- OWASP ZAP baseline DAST run — impact M (would add dynamic coverage) — grade B — OUT: the Week-1 required minimum is one SAST or DAST tool, and adding DAST before SAST artifacts work makes the demo less reliable; reconsider after Week-1.
- Ground-truth mapping and precision/recall calculation — impact H (needed for an honest comparison) — grade B — OUT: it depends on stable Week-1 raw output and belongs to Week 2 data work.
- API gateway/allowlist for agent-generated requests — impact H in the final system — grade B — OUT: explicitly reserved for Week 4; there will be no active testing requests in Week 1.

## Cut list (NOT in v1 — deferred, not deleted)

- Automatic ground-truth scoring, false-positive/false-negative metrics, ablation study — deferred to Week 2 after normalized data and evaluation protocol exist.
- AI agent, RAG/knowledge base, LLM-as-a-judge, prompt-injection defenses — deferred to Weeks 2–5; no LLM is needed to prove scanner output.
- API gateway, any automated active requests, and destructive/exploit payloads — deferred to Week 4; the Week-1 target stays bound to localhost.
- Web UI, database, multi-agent orchestration, GraphRAG, vLLM/GPU deployment — out of this Week-1 scope because none proves the required scanner evidence.

## Decision

GO — the Week-1 slice is small enough to validate with two pinned SAST tools and real artifacts, and it directly supplies the stable raw data required by Week 2.
