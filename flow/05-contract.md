# Stage 05 — Interface Contract (the seam)

The contract is whatever sits between your core and its consumer. For a web app that's
API endpoints (the table below). For a CLI it's commands + flags + output shapes; for a
plugin it's hooks + filters; for a pipeline it's input/output file schemas. Keep the
table's SPIRIT — every feature maps to an interface, every interface has its shapes
written before code — and adapt the columns to your project's shape.

Written BEFORE any code. Backend cards build TO this table; UI cards consume FROM it.
The #1 AI-build failure is producer/consumer drift — backend ships one shape, UI assumes
another, both look green. This file is the cheap fix.

## Gate — check ALL before `/flow next`
- [x] Every PRD feature maps to at least one INTERFACE below (web: endpoint · cli: command · library: public function · skill: command/file)
- [x] Every interface has its INPUT and OUTPUT shapes written (web: request+response · cli: flags+output/exit code · library: args+return)
- [x] Access/effects column filled for every interface (web: public/token/admin · non-web: writes/side-effects, or "none")
- [x] No FILL placeholders remain in this file

## OpenAPI / Swagger rule  (web only — N/A for cli/library/skill)

For non-web types there is no served spec; the equivalent "no producer/consumer drift" check
is the per-type done-evidence (the command runs / the API imports / the skill installs+runs).
For `web`:

This table is the PLANNING source of truth. If the framework serves a spec (FastAPI →
`/openapi.json` + `/docs`), the served spec is the RUNTIME artifact of this same contract:
- Path/method/shapes here and in the served spec must agree — the contract-test card
  asserts every endpoint in this table exists in the live `/openapi.json` with matching
  request/response shapes.
- Change flows ONE way: amend this file first, then the code, then the spec follows.
- **Docs land with the API, not after**: the served spec is live from the vertical-slice
  card onward, and every backend card's verify checks its endpoints appear in the live
  `/docs` with correct schemas. The contract-test card later asserts full agreement —
  but by then the docs have been growing card by card, never a catch-up task.
- Keep `/docs` enabled at least until v1 ships — it's the free human-readable contract.

## Interfaces  (web: endpoints · cli: commands · library: functions · skill: commands)

Adapt the columns to your project type. Web: Method/Path/Access(=auth: public/token/admin)/
Request/Response. CLI: Command/Flags/Access(=side-effects)/Input/Output+exit. Library:
Function/—/Access(=none)/Args/Return. The shared column below is "Access/Effects".

| Method/Interface | Path/Name | Access/Effects | Input shape | Output shape |
|---|---|---|---|---|
| Make target-up | `make target-up` | Starts/reuses one Docker Compose `webgoat` container; binds `127.0.0.1:8080` and `127.0.0.1:9090` only. | Checked-in `docker-compose.yml`; Docker daemon. | Exit `0` only after `GET /WebGoat/actuator/health` yields HTTP 200. On success print `http://127.0.0.1:8080/WebGoat/`; nonzero for Docker/health failure. |
| Make target-down | `make target-down` | Stops the local WebGoat Compose service and its project network. | Checked-in Compose file; Docker daemon. | Exit `0` after Compose stops/removes the service; no report files are deleted. |
| Make scan-opengrep | `make scan-opengrep` | Read-only scan of `targets/webgoat` using OpenGrep `v1.26.0` and checked-in rules; writes only `results/raw/opengrep.json`. | Git submodule at `v2025.3`; `rules/opengrep/*.yaml`; scanner image/version pins. | Exit `0` if OpenGrep completes and the report parses as JSON, regardless of finding count; nonzero for setup/scanner/JSON-validation error. |
| Make scan-findsecbugs | `make scan-findsecbugs` | Compiles the pinned WebGoat source and scans its bytecode with FindSecBugs `1.14.0`; writes only `results/raw/findsecbugs.sarif`. | Git submodule at `v2025.3`; Maven wrapper; scanner image/version pins. | Exit `0` if build and scan complete and the report parses as JSON with SARIF `version` and `runs`; nonzero for build/scanner/SARIF-validation error. |
| Make scan | `make scan` | Runs both SAST interfaces sequentially and creates both raw outputs. | Inputs of `scan-opengrep` and `scan-findsecbugs`. | Exit `0` only if both component commands return `0`; prints both output paths. |
| GitHub Actions workflow | `.github/workflows/security-scan.yml` | Runs `make scan` in the CI runner and uploads the two raw report files; it never deploys WebGoat or sends active requests. | Repository checkout with submodules; Docker; committed scanner configuration. | Green workflow and one artifact containing exactly `opengrep.json` and `findsecbugs.sarif`; nonzero on operational/validation failure, not merely because findings exist. |
| README | `README.md` | Read-only documentation interface for all FR1–FR5 commands, endpoint list, artifact paths, and limitations. | Checked-in repository and release links. | A new contributor can copy each documented command without undisclosed credentials; no executable side effect. |

## Shared shapes (objects used by multiple interfaces)

```
`results/raw/opengrep.json` is OpenGrep native JSON: top-level object with `version`, `results[]`, and `errors[]`; each result retains rule id, path, start/end position, message, severity, and metadata when supplied by the rule.

`results/raw/findsecbugs.sarif` is native SARIF JSON: top-level `{ "version": "2.1.0", "runs": [...] }`; each run retains tool driver/rule metadata and findings in `results[]`.

All scan interfaces use exit `0` only for a completed, parseable report (findings are data); a nonzero exit indicates an operational failure. Version pins and source provenance live in committed configuration/submodule metadata, not in the generated report paths.
```

## Feature → interface map

Reference each PRD feature by its `FRn` id so the mapping is machine-checkable
(`/flow consistency` flags any `FRn` with no interface here).

- FR1 → `make target-up`, `make target-down`, `docker-compose.yml`.
- FR2 → `make scan-opengrep`, `results/raw/opengrep.json`.
- FR3 → `make scan-findsecbugs`, `results/raw/findsecbugs.sarif`.
- FR4 → `.github/workflows/security-scan.yml`, `make scan`.
- FR5 → `README.md`, all documented Make interfaces.
