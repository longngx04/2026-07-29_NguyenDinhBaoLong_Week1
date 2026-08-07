# Project Sentinel — Folder Structure Refactor Guide for AI Coding Agents

> **Document type:** Execution contract for AI coding agents  
> **Primary goal:** Reorganize the repository from a week-based layout into a product-oriented layout without changing observable behavior.  
> **Repository:** `longngx04/2026-07-29_NguyenDinhBaoLong_Week3`  
> **Scope:** Folder structure, module paths, build/test/runtime paths, documentation links, reports, generated artifacts, and agent-instruction cleanup.

---

## 1. Role and operating mode

You are acting as a **Senior Python Architect and repository maintainer**.

Your task is not merely to rename directories. You must perform a controlled repository migration that:

1. Makes the project understandable within five minutes.
2. Organizes production code by stable responsibility rather than internship week.
3. Preserves historical reports by week.
4. Separates human-readable documentation from machine-generated data and outputs.
5. Preserves all existing working commands or replaces them with clearly documented equivalents.
6. Leaves the repository in a testable, reviewable, and maintainable state.

Treat this work as a **behavior-preserving refactor**. Do not redesign business logic, prompts, security rules, schemas, LLM behavior, or finding semantics unless a minimal change is required to repair imports or paths.

---

## 2. Current repository problem

The current repository mixes two incompatible organization models:

- Timeline-based code: `week2/`, `week3/`, `tests/week3/`, `fixtures/week3/`.
- Responsibility-based resources: `knowledge/`, `prompts/`, `rules/`, `schemas/`, `results/`, `scanner/`, `scripts/`.

This makes it unclear whether a developer should locate code by week or by system capability. Code is shared and evolves across weeks, while reports are historical snapshots and should remain week-based.

### Architectural rule

> **Production code is organized by capability. Historical reports are organized by week.**

After the migration, folders named `week2`, `week3`, `week4`, etc. must not be used as Python packages or test namespaces. Week identifiers may remain only in historical reporting, release notes, or explicitly versioned evidence.

---

## 3. Mandatory preflight inspection

Before changing any file, inspect the repository and record a concise baseline.

### 3.1 Read these files first

At minimum, inspect:

- `README.md`
- `AGENTS.md`
- Every applicable instruction file under `.agents/`
- `pyproject.toml`
- `Makefile`
- `.gitignore`
- `.gitmodules`
- `docker-compose.yml`
- `.github/workflows/*`
- `scripts/*`
- Every Python file under `week2/` and `week3/`
- Every test under `tests/`
- Existing schemas, prompts, knowledge files, fixtures, and committed results

### 3.2 Build a dependency inventory

Identify all references to old paths before moving files:

```bash
grep -RInE '\bweek2\b|\bweek3\b|tests/week3|fixtures/week3|results/|knowledge/|prompts/|rules/opengrep|scanner/|targets/' \
  --exclude-dir=.git .
```

Also inspect Python imports:

```bash
grep -RInE '^(from|import) (week2|week3)' \
  --include='*.py' --exclude-dir=.git .
```

### 3.3 Capture baseline behavior

Run every command that can execute safely in the current environment. At minimum attempt:

```bash
python3 --version
python3 -m pytest -q
make agent-test
make analyze-mock
make validate-analysis
```

If dependencies or generated inputs are missing, record the exact limitation. A pre-existing failure is not permission to ignore testing. After the refactor, the agent must prove that it introduced no additional failure.

### 3.4 Protect the worktree

Before moving files:

```bash
git status --short
git branch --show-current
git diff --stat
git diff
```

Rules:

- Never discard unrelated user changes.
- Never run `git reset --hard`, `git clean -fd`, or destructive equivalents.
- Do not push, force-push, merge, or rewrite history.
- Prefer working on `refactor/repository-structure` when branch creation is permitted.
- Do not create a commit unless the user explicitly requested a commit.

---

## 4. Non-negotiable constraints

### 4.1 Preserve behavior

The following behavior must remain equivalent:

- OpenGrep scan workflow.
- Finding normalization.
- Knowledge search/retrieval.
- Fake LLM and real OpenRouter provider boundaries.
- Analysis pipeline, grouping, evidence, prompt construction, validation, JSONL output, and summary output.
- JSON Schema validation.
- WebGoat submodule behavior.
- Loopback-only exposure of the vulnerable target.
- Offline test behavior.

### 4.2 Preserve historical evidence

- Do not rewrite the substantive content of completed weekly reports merely to improve style.
- Path and link corrections are allowed.
- Historical output selected as sprint evidence may be moved into the corresponding report folder.
- Never silently overwrite historical artifacts with newly generated output.

### 4.3 Preserve security boundaries

- Do not commit `.env` or API keys.
- Do not print secrets in logs.
- Do not weaken schema validation.
- Do not remove provenance/evidence checks to make tests pass.
- Do not allow WebGoat or another vulnerable service to bind publicly.
- Do not introduce network calls into offline unit tests.

### 4.4 Avoid speculative redesign

Do not:

- Add a framework that the project does not need.
- Convert the project to a monorepo.
- Introduce dependency injection frameworks.
- Split each Python file into a separate package without a clear architectural reason.
- Rename domain concepts merely for stylistic preference.
- Modify LLM model selection, prompts, thresholds, schema meaning, or security rules as part of this task.

---

## 5. Required target structure

Use the following structure as the target. Minor adjustments are allowed only when the actual dependency graph provides a clear reason. Document every deviation.

```text
project-sentinel/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── security-scan.yml
│
├── .agents/
│   ├── review.md
│   └── security.md
│
├── artifacts/                         # Runtime-generated output; mostly gitignored
│   ├── raw/
│   ├── normalized/
│   └── analysis/
│
├── benchmarks/
│   └── targets/
│       └── webgoat/                   # Existing Git submodule
│
├── configs/
│   ├── opengrep/
│   │   └── java-security.yml
│   └── prompts/
│       └── security-analysis-system.md
│
├── data/
│   └── knowledge-base/
│       ├── owasp/
│       ├── tools/
│       └── vulnerabilities/
│
├── docs/
│   ├── architecture.md
│   ├── development.md
│   └── decisions/
│
├── infra/
│   └── docker/
│       └── scanner/
│           └── Dockerfile
│
├── reports/
│   ├── week-01/
│   │   ├── report.md
│   │   └── artifacts/
│   ├── week-02/
│   │   ├── report.md
│   │   └── artifacts/
│   └── week-03/
│       ├── report.md
│       └── artifacts/
│
├── schemas/
│   ├── finding.schema.json
│   └── security-analysis-record.schema.json
│
├── scripts/
│   └── scan-opengrep.sh
│
├── src/
│   └── project_sentinel/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       │
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── analyzer.py
│       │   ├── evidence.py
│       │   ├── grouping.py
│       │   ├── packet_builder.py
│       │   ├── pipeline.py
│       │   ├── prompt_builder.py
│       │   └── validators.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── input_loader.py
│       │   └── normalizer.py
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── factory.py
│       │   ├── fake.py
│       │   └── openrouter.py
│       │
│       └── retrieval/
│           ├── __init__.py
│           ├── keyword_search.py
│           └── knowledge_retriever.py
│
├── tests/
│   ├── unit/
│   │   ├── analysis/
│   │   ├── ingestion/
│   │   ├── llm/
│   │   └── retrieval/
│   ├── integration/
│   └── fixtures/
│       ├── findings/
│       └── expected/
│
├── .env.example
├── .gitignore
├── .gitmodules
├── AGENTS.md
├── CLAUDE.md                         # Optional; thin pointer to AGENTS.md
├── Makefile
├── README.md
├── docker-compose.yml
└── pyproject.toml
```

---

## 6. Folder semantics

The agent must enforce the following meanings consistently.

| Folder | Purpose | Must not contain |
|---|---|---|
| `src/project_sentinel/` | Importable production Python code | Reports, fixtures, generated results |
| `tests/unit/` | Fast, deterministic, offline tests | Real network/API calls |
| `tests/integration/` | Cross-module and provider-boundary tests | Unmarked expensive tests |
| `tests/fixtures/` | Small deterministic test inputs/expected outputs | Full benchmark datasets or runtime output |
| `data/knowledge-base/` | Curated knowledge consumed by the system | Test-only fixtures and generated output |
| `configs/` | Human-authored runtime configuration, prompts, scanner rules | Runtime output |
| `schemas/` | Machine-readable contracts | Python implementation logic |
| `artifacts/` | Current/local generated output | Source code and historical reports |
| `reports/week-XX/` | Immutable human-readable sprint history | Active production modules |
| `reports/week-XX/artifacts/` | Selected evidence frozen for that sprint | Arbitrary local runs |
| `benchmarks/targets/` | Benchmark/vulnerable target projects | Project Sentinel production code |
| `infra/` | Docker and deployment/runtime infrastructure | Python domain logic |
| `docs/` | Long-lived technical documentation | Weekly status reports |
| `.agents/` | Minimal specialized agent rules | Duplicated project architecture and long plans |

---

## 7. Required source-file migration map

Use `git mv` whenever possible so history remains recognizable.

### 7.1 Week 2 package

| Current path | Target path |
|---|---|
| `week2/normalize.py` | `src/project_sentinel/ingestion/normalizer.py` |
| `week2/schema.py` | Merge carefully into `src/project_sentinel/models.py`, or keep as `src/project_sentinel/finding_schema.py` if responsibilities are materially different |
| `week2/search.py` | `src/project_sentinel/retrieval/keyword_search.py` |
| `week2/__init__.py` | Remove after package migration |

### 7.2 Week 3 package

| Current path | Target path |
|---|---|
| `week3/analyzer.py` | `src/project_sentinel/analysis/analyzer.py` |
| `week3/evidence.py` | `src/project_sentinel/analysis/evidence.py` |
| `week3/grouping.py` | `src/project_sentinel/analysis/grouping.py` |
| `week3/packet_builder.py` | `src/project_sentinel/analysis/packet_builder.py` |
| `week3/pipeline.py` | `src/project_sentinel/analysis/pipeline.py` |
| `week3/prompt_builder.py` | `src/project_sentinel/analysis/prompt_builder.py` |
| `week3/validators.py` | `src/project_sentinel/analysis/validators.py` |
| `week3/input_loader.py` | `src/project_sentinel/ingestion/input_loader.py` |
| `week3/retrieval.py` | `src/project_sentinel/retrieval/knowledge_retriever.py` |
| `week3/llm/` | `src/project_sentinel/llm/` |
| `week3/cli.py` | `src/project_sentinel/cli.py` |
| `week3/config.py` | `src/project_sentinel/config.py` |
| `week3/models.py` | `src/project_sentinel/models.py` |
| `week3/main.py` | Remove if redundant; otherwise preserve as a thin compatibility entry point or merge into `cli.py` |
| `week3/__init__.py` | Remove after package migration |

### 7.3 Important mapping rule

Do not blindly concatenate files. Before merging `week2/schema.py` and `week3/models.py`, inspect:

- Class and function name conflicts.
- Serialization behavior.
- Validation assumptions.
- Import cycles.
- Tests that patch module-qualified paths.

Prefer the smallest safe arrangement. A single `models.py` is acceptable for the current project size, but correctness is more important than forcing a single file.

---

## 8. Required non-code migration map

| Current path | Target path | Rule |
|---|---|---|
| `tests/week3/` | Split into `tests/unit/` and `tests/integration/` | Organize by tested capability, not week |
| `fixtures/week3/` | `tests/fixtures/findings/` or `tests/fixtures/expected/` | Rename files by scenario |
| `knowledge/` | `data/knowledge-base/` | Preserve content and repair loaders |
| `prompts/` | `configs/prompts/` | Preserve prompt text unless path repair is required |
| `rules/opengrep/` | `configs/opengrep/` | Preserve rule semantics |
| `scanner/Dockerfile` | `infra/docker/scanner/Dockerfile` | Repair build contexts and Compose/workflow paths |
| `targets/webgoat/` | `benchmarks/targets/webgoat/` | Preserve Git submodule identity |
| `docs/report-week1.md` | `reports/week-01/report.md` | Do not rewrite historical result content |
| `docs/report-week2.md` | `reports/week-02/report.md` | Do not rewrite historical result content |
| `docs/report-week3.md` | `reports/week-03/report.md` | Do not rewrite historical result content |
| `results/raw/` | `artifacts/raw/` | Local/generated; normally gitignored |
| `results/normalized/` | `artifacts/normalized/` | Active runtime output |
| `results/analysis/` | `artifacts/analysis/` | Active runtime output |

### 8.1 Historical artifact rule

Some currently committed results may represent sprint deliverables. Handle them as follows:

1. Determine which files were intentionally committed as Week 1, Week 2, or Week 3 evidence.
2. Move a frozen copy or the tracked artifact into the matching `reports/week-XX/artifacts/` folder.
3. Configure active commands to write new output to root `artifacts/`.
4. Ensure running a command does not mutate historical report artifacts.
5. Do not duplicate large files unless the distinction between runtime output and historical evidence requires it.

Recommended examples:

```text
reports/week-02/artifacts/normalized-findings.json
reports/week-03/artifacts/security-analysis.jsonl
reports/week-03/artifacts/run-summary.json
```

---

## 9. Migration execution plan

Perform the refactor in small, verifiable phases. Do not move everything and repair afterward.

### Phase 0 — Baseline and change plan

Create an internal checklist containing:

- Current commands and their status.
- Current import graph.
- Existing generated/committed artifacts.
- All path references found by grep.
- Exact files planned for move, merge, retention, or deletion.

Do not create a large speculative design document. Keep the checklist concise and executable.

### Phase 1 — Create the stable skeleton

Create only the folders needed by the migration:

```bash
mkdir -p \
  src/project_sentinel/{analysis,ingestion,llm,retrieval} \
  tests/{unit,integration,fixtures/findings,fixtures/expected} \
  configs/{opengrep,prompts} \
  data/knowledge-base/{owasp,tools,vulnerabilities} \
  reports/week-{01,02,03}/artifacts \
  artifacts/{raw,normalized,analysis} \
  benchmarks/targets \
  infra/docker/scanner \
  docs/decisions
```

Add required `__init__.py` files to importable Python packages.

Do not add `.gitkeep` when a real file can document the folder. For ignored runtime directories, a small `README.md` explaining the directory contract is preferable when visibility is necessary.

### Phase 2 — Migrate the Python package

1. Move modules with `git mv`.
2. Repair imports immediately after each logical group.
3. Run targeted tests for that group.
4. Avoid compatibility shims unless an external interface truly depends on old module paths.
5. Remove empty `week2/` and `week3/` only after all imports and commands are updated.

Expected new imports:

```python
from project_sentinel.analysis.pipeline import AnalysisPipeline
from project_sentinel.ingestion.normalizer import normalize_findings
from project_sentinel.retrieval.keyword_search import search_knowledge
from project_sentinel.llm.factory import create_llm
```

The exact symbol names must match the implementation. Do not invent or rename public functions without need.

### Phase 3 — Update packaging

Update `pyproject.toml` to use `src` layout.

Minimum expected configuration:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "project-sentinel"
version = "0.1.0"
description = "Security finding normalization and AI-assisted analysis pipeline"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "jsonschema>=4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]

[project.scripts]
project-sentinel = "project_sentinel.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
include = ["project_sentinel*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--import-mode=importlib",
    "--strict-config",
    "--strict-markers",
]
```

Adjust only when the current code requires a justified difference.

Verify editable installation:

```bash
python3 -m pip install -e '.[dev]'
python3 -c 'import project_sentinel; print(project_sentinel.__file__)'
project-sentinel --help
```

Do not rely on adding the repository root to `PYTHONPATH` as a permanent fix.

### Phase 4 — Update commands and runtime paths

Update `Makefile` so it invokes the new package and writes active output under `artifacts/`.

Expected direction:

```make
agent-test:
	@LLM_PROVIDER=fake python3 -m pytest -q tests

normalize:
	@python3 -m project_sentinel.cli normalize \
		--input artifacts/raw/opengrep.json \
		--output artifacts/normalized/findings.json

search:
	@test -n "$(Q)" || (printf '%s\n' 'Usage: make search Q='\''SQL Injection'\''' >&2; exit 1)
	@python3 -m project_sentinel.cli search --query "$(Q)"

analyze:
	@python3 -m project_sentinel.cli analyze \
		--input artifacts/normalized/findings.json \
		--output artifacts/analysis/security-analysis.jsonl \
		--summary artifacts/analysis/run-summary.json

analyze-mock:
	@python3 -m project_sentinel.cli analyze \
		--input tests/fixtures/findings/valid.json \
		--provider fake \
		--output artifacts/analysis/security-analysis.jsonl \
		--summary artifacts/analysis/run-summary.json

validate-analysis:
	@python3 -m project_sentinel.cli validate \
		--input artifacts/analysis/security-analysis.jsonl
```

This is an architectural target, not permission to invent unsupported CLI subcommands. If the existing CLI does not expose `normalize` or `search`, either:

- Add thin CLI adapters that reuse existing functions without changing semantics, or
- Retain module entry commands under the new package, for example:

```bash
python3 -m project_sentinel.ingestion.normalizer
python3 -m project_sentinel.retrieval.keyword_search "SQL Injection"
```

Choose the smallest coherent solution and document it.

Update all path references in:

- `Makefile`
- `scripts/*`
- `docker-compose.yml`
- `.github/workflows/*`
- `.gitmodules`
- `.gitignore`
- `README.md`
- `AGENTS.md` and `.agents/*`
- Python constants/defaults
- Tests and fixtures

### Phase 5 — Migrate tests and fixtures

Classify each existing test:

- **Unit:** one module or small collaboration; no real network; no real LLM provider.
- **Integration:** full pipeline, filesystem contract, CLI process, Docker boundary, or real provider boundary.

Naming rules:

```text
tests/unit/analysis/test_grouping.py
tests/unit/analysis/test_validators.py
tests/unit/llm/test_fake.py
tests/unit/retrieval/test_keyword_search.py
tests/integration/test_analysis_pipeline.py
tests/integration/test_cli.py
```

Fixture rules:

- Replace generic names such as `valid-findings.json` with scenario-oriented names when safe.
- Keep fixtures small and deterministic.
- Do not use historical report artifacts as mutable test fixtures.
- Tests must resolve paths independently of the current shell working directory.
- Prefer `pathlib.Path` and paths relative to a known project/package/test location.

When tests patch imports by string, update the patch target to where the symbol is looked up after migration.

### Phase 6 — Reports and documentation

Move weekly reports into:

```text
reports/week-01/report.md
reports/week-02/report.md
reports/week-03/report.md
```

Each report folder may contain `artifacts/` for frozen machine-readable evidence.

Do not substantially rewrite completed reports. Only:

- Repair broken links.
- Repair moved paths.
- Add an artifact index when useful.
- Normalize the folder and filename.

Create or update long-lived documents:

#### `docs/architecture.md`

Must explain briefly:

```text
OpenGrep
  -> normalization
  -> knowledge retrieval
  -> security analysis
  -> schema validation
  -> JSONL and summary output
```

Include module ownership and important security boundaries. Do not repeat the entire README.

#### `docs/development.md`

Must contain:

- Setup.
- Editable install.
- Common Make targets.
- Test commands.
- Artifact lifecycle.
- Rule that reports are historical and active code is not organized by week.

#### `README.md`

Keep it optimized for a five-minute review:

1. What the project does.
2. Pipeline overview.
3. Repository structure.
4. Quick start.
5. Common commands.
6. Tests.
7. Links to weekly reports.
8. Security note about WebGoat loopback binding.

Do not turn the README into a chronological implementation diary.

### Phase 7 — Simplify agent instructions

The current agent-instruction system must not require every agent to read many overlapping files.

Target:

```text
AGENTS.md
.agents/
├── review.md
└── security.md
CLAUDE.md          # Optional thin pointer
```

#### `AGENTS.md` should be the primary source

Include only stable instructions:

- Project overview.
- Repository structure.
- Setup/test commands.
- Coding rules.
- Security invariants.
- Rule that historical reports must not be overwritten.
- Definition of Done.
- Handoff expectations.

#### `.agents/review.md`

Consolidate:

- Diff review checklist.
- Severity definitions.
- Escalation conditions.
- Requirement to review changed files and impacted contracts.

#### `.agents/security.md`

Consolidate:

- Secret handling.
- Offline test boundary.
- WebGoat loopback-only rule.
- Schema and provenance validation rules.
- No weakening security checks to pass tests.

#### `CLAUDE.md`

When kept, it must be thin:

```md
# Claude Instructions

Read and follow `AGENTS.md`.

Additional specialized rules:

- `.agents/review.md`
- `.agents/security.md`
```

Before deleting old `.agents` files:

1. Extract every still-valid requirement.
2. Move it into the correct surviving file.
3. Remove duplicates and contradictions.
4. Repair references.
5. Confirm no workflow depends on the removed file.

Do not preserve obsolete model names or vendor-specific preferences as architectural rules unless the user explicitly wants them retained.

### Phase 8 — Cleanup and final verification

Only after all tests and path checks pass:

- Remove empty old directories.
- Remove obsolete duplicate entry points.
- Remove stale documentation that has been fully migrated.
- Do not add `old/`, `backup/`, or `archive/` folders. Git history is the archive.

Run stale-reference searches:

```bash
grep -RInE '\bweek2\b|\bweek3\b|tests/week3|fixtures/week3' \
  --exclude-dir=.git . || true

grep -RInE 'results/|knowledge/|prompts/|rules/opengrep|scanner/|targets/webgoat' \
  --exclude-dir=.git . || true

grep -RInE '^(from|import) (week2|week3)' \
  --include='*.py' --exclude-dir=.git . || true
```

Any remaining match must be either:

- Historical prose that is intentionally retained, or
- An error that must be repaired.

Document intentional remaining matches.

---

## 10. Git submodule handling

`targets/webgoat/` is a Git submodule. Moving it requires special care.

Required procedure:

1. Inspect `.gitmodules` and the Git index entry.
2. Use `git mv targets/webgoat benchmarks/targets/webgoat` when supported.
3. Update `.gitmodules` path only; preserve the original submodule URL and pinned commit.
4. Synchronize and validate:

```bash
git submodule sync --recursive
git submodule status --recursive
git submodule update --init --recursive
```

5. Update Docker Compose, scripts, Makefile, CI, and documentation references.
6. Do not replace the submodule with a copied directory.
7. Do not update the submodule revision as part of this refactor.

---

## 11. `.gitignore` policy

Ensure the following are ignored where appropriate:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/

artifacts/raw/*
artifacts/normalized/*
artifacts/analysis/*
```

Do not ignore:

- `reports/week-XX/report.md`
- Historical evidence intentionally committed under `reports/week-XX/artifacts/`
- Schemas, prompts, knowledge-base documents, scanner rules, tests, or fixtures

If empty artifact folders must be visible, use a tracked `README.md` explaining their purpose rather than tracking generated files.

---

## 12. Compatibility policy

Prefer a clean migration over permanent duplicate packages.

Temporary compatibility wrappers are allowed only when:

- An external interface outside the repository may still import `week2` or `week3`.
- CI or a consumer cannot be updated in the same change.
- The wrapper is clearly marked for removal and contains no duplicated logic.

Do not keep complete copies of both old and new packages.

A compatibility wrapper, when truly required, should be minimal:

```python
"""Temporary compatibility import. Remove after downstream migration."""

from project_sentinel.analysis.pipeline import AnalysisPipeline

__all__ = ["AnalysisPipeline"]
```

For this repository, the default decision should be to update all in-repo callers and remove the week packages.

---

## 13. Required verification matrix

The refactor is incomplete until this matrix is evaluated.

| Area | Verification |
|---|---|
| Package | `import project_sentinel` succeeds from an editable install |
| CLI | `project-sentinel --help` or documented module CLI succeeds |
| Unit tests | All unit tests pass offline |
| Integration tests | All runnable integration tests pass |
| Fake LLM | Fake provider requires no network or API key |
| Real provider boundary | Configuration still reads API key securely; no key committed |
| Normalize | Existing input produces schema-compatible normalized findings |
| Search/retrieval | Existing knowledge queries still return equivalent results |
| Analyze mock | Fixture analysis produces JSONL and summary |
| Validate | Generated JSONL passes the existing JSON Schema |
| OpenGrep | Scan command still points to valid rule, target, and output paths |
| Docker | Compose resolves updated Dockerfile/build contexts |
| Submodule | WebGoat remains a valid submodule at the same revision |
| CI | Workflow paths and commands match the new layout |
| Reports | Week reports and frozen artifacts are reachable from README |
| Artifacts | Active runs write to `artifacts/`, not historical report folders |
| Stale refs | No accidental runtime/import references to old layout remain |

Recommended command sequence:

```bash
python3 -m pip install -e '.[dev]'
python3 -m pytest -q
make agent-test
make analyze-mock
make validate-analysis

git submodule status --recursive
docker compose config >/dev/null

# Run when prerequisites are available:
make normalize
make search Q='SQL Injection'
make analyze-offline-full
```

If `make scan` requires Docker or a large target and cannot be executed, at minimum validate:

- `docker compose config`
- Shell syntax for scripts: `bash -n scripts/*.sh`
- Correct existence of referenced paths
- CI command consistency

---

## 14. Definition of Done

The task is complete only when every applicable item below is true.

### Structure

- [ ] Production Python code exists only under `src/project_sentinel/`.
- [ ] No active Python package is named after a week.
- [ ] Tests are organized under `tests/unit/` and `tests/integration/`.
- [ ] Test data is under `tests/fixtures/`.
- [ ] Curated knowledge is under `data/knowledge-base/`.
- [ ] Prompts and scanner rules are under `configs/`.
- [ ] Runtime output is under `artifacts/`.
- [ ] Weekly reports are under `reports/week-XX/`.
- [ ] The WebGoat target is under `benchmarks/targets/` and remains a submodule.
- [ ] Docker scanner infrastructure is under `infra/`.

### Behavior

- [ ] No intended functionality was removed.
- [ ] Existing relevant tests pass, or pre-existing failures are explicitly distinguished from new failures.
- [ ] Mock/offline analysis still works without an API key.
- [ ] Validation still rejects invalid records.
- [ ] Generated output paths do not overwrite historical evidence.
- [ ] WebGoat remains loopback-only.

### Tooling

- [ ] `pyproject.toml` uses `src` layout.
- [ ] Editable installation succeeds.
- [ ] Make targets reference the new paths.
- [ ] CI workflows reference the new paths.
- [ ] Docker Compose resolves successfully.
- [ ] Shell scripts pass syntax checking.
- [ ] `.gitignore` matches the new artifact lifecycle.

### Documentation

- [ ] README explains the project in five minutes or less.
- [ ] README links to all weekly reports.
- [ ] `docs/architecture.md` matches the actual modules.
- [ ] `docs/development.md` contains current commands.
- [ ] `AGENTS.md` is the primary agent instruction source.
- [ ] Redundant agent instruction files have been safely consolidated.
- [ ] No broken internal links remain.

### Hygiene

- [ ] No `.env`, API keys, tokens, or secrets are included.
- [ ] No `old/`, `backup/`, `final-final/`, or duplicated code trees were created.
- [ ] No unrelated user changes were overwritten.
- [ ] No unintentional references to `week2/`, `week3/`, `tests/week3/`, or `fixtures/week3/` remain.

---

## 15. Prohibited shortcuts

The following are unacceptable:

1. Moving folders without repairing imports, tests, CI, Makefile, and documentation.
2. Making tests pass by deleting assertions or disabling validation.
3. Keeping both `week3/` and `src/project_sentinel/` as duplicated implementations.
4. Copying the WebGoat submodule as normal files.
5. Writing active output into `reports/week-XX/artifacts/`.
6. Reformatting or rewriting all report content as part of a structure-only refactor.
7. Adding unnecessary dependencies to solve path problems.
8. Hardcoding absolute local paths.
9. Using `sys.path.insert(...)` as the permanent packaging strategy.
10. Silently deleting files whose purpose is unclear.
11. Claiming success without running verification commands.
12. Reporting only “tests passed” without showing which commands ran.

---

## 16. Expected final handoff from the implementing agent

At completion, provide a concise handoff in the following format.

```md
# Repository Structure Refactor — Handoff

## Outcome
- One or two sentences describing the result.

## Final structure
- Summarize the major top-level folders.

## Files moved
| Old path | New path | Notes |
|---|---|---|

## Files merged or removed
| File | Action | Reason |
|---|---|---|

## Compatibility changes
- Import changes.
- CLI/Make target changes.
- Runtime output path changes.

## Verification
| Command | Result |
|---|---|
| `python3 -m pytest -q` | PASS/FAIL with counts |
| `make agent-test` | PASS/FAIL |
| `make analyze-mock` | PASS/FAIL |
| `make validate-analysis` | PASS/FAIL |
| `docker compose config` | PASS/FAIL |
| `git submodule status --recursive` | PASS/FAIL |

## Known limitations
- Only real limitations, including pre-existing failures or unavailable services.

## Remaining stale references
- List intentional historical references, or state `None`.

## Git diff summary
- Changed-file count.
- Insertions/deletions.
- Confirmation that no secret or unrelated change was included.
```

The handoff must be based on actual command output. Do not fabricate test results.

---

## 17. Final directive to the coding agent

Execute the migration end to end. Make the smallest set of architectural changes necessary to achieve the target organization while preserving behavior.

Prioritize in this order:

1. Safety and preservation of user work.
2. Behavior and security invariants.
3. Correct package/import/runtime paths.
4. Testability and reproducibility.
5. Repository readability.
6. Cleanup and cosmetic consistency.

Do not stop after proposing a structure. Apply the changes, repair all references, run the available verification suite, inspect the final diff, and provide the required handoff.
