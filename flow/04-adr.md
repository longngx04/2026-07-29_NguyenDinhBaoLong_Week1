# Stage 04 — ADR (architecture decisions)

Short. The most valuable section is what you are NOT doing and why.

## Gate — check ALL before `/flow next`
- [x] Each decision has a one-line "why" and a one-line "what I rejected"
- [x] The NOT-doing list is written
- [x] Decisions cover: data storage, auth approach, deploy target
- [x] No FILL placeholders remain in this file

## Decisions

| # | Decision | Why | Rejected alternative |
|---|---|---|---|
| 1 | Store Week-1 raw reports as ignored local files and GitHub Actions artifacts; do not introduce a database. | Raw JSON/SARIF are the source evidence for Week 2, while a database/schema would be unvalidated extra work. | Normalizing into a custom JSON schema or storing findings in a database now; that is a Week-2 decision. |
| 2 | No Sentinel user authentication in Week 1; constrain the intentionally vulnerable WebGoat service to `127.0.0.1` and use no repository secrets. | The scanner pipeline has no external user-facing interface, and localhost binding minimizes target exposure. | Public deployment, a custom login system, API keys, or relying on WebGoat lesson credentials as Sentinel auth. |
| 3 | Run WebGoat through local Docker Compose and execute scans in GitHub Actions; retain artifacts instead of deploying a service. | This is the least-privilege, reproducible environment that meets the Week-1 demo requirement. | Exposing WebGoat on a public VM, Kubernetes, or a hosted dashboard. |
| 4 | Pin WebGoat source submodule and runtime image to release `v2025.3`; record OpenGrep `v1.26.0` and FindSecBugs `1.14.0`. | A comparison is meaningless if target/tool versions drift between local and CI runs. | Floating `main`, `latest`, or remote rule packs resolved afresh at every scan. |
| 5 | Keep OpenGrep's native JSON and FindSecBugs' native SARIF as separate raw inputs. | Each file preserves the tool's original evidence and metadata for Week-2 normalization. | Converting SARIF into an ad-hoc JSON shape during Week 1, which would hide or pre-judge baseline data. |

## NOT doing in v1 (and why it's safe to skip)

- No DAST, active HTTP testing, API Gateway, or exploit payloads: these require the Week-4 allowlist and safety controls.
- No AI agent, LLM judge, RAG, or knowledge base: these consume raw findings only after Week-2 normalization.
- No public WebGoat endpoint, cloud target, or target credentials in Git: WebGoat remains a local authorized lab.
- No false-positive/false-negative or ablation claims: an evaluation protocol and ground-truth mapping must precede those claims in Week 2.
