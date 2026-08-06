# Project Sentinel — Week 3 Report

> **Security Analysis Agent (Evidence-Grounded AI Analysis)**

---

## 1. Executive Summary & Design Checkpoint (Phase 0)

### 1.1 Baseline Statistics
- **Input findings source**: `results/normalized/findings.json`
- **Total findings**: 23
- **Severity distribution**: 20 High (ERROR), 2 Medium (WARNING), 1 Low (INFO)
- **Baseline validation**: `make normalize` and `make search Q="SQL Injection"` verified and operational.

---

## 2. Grouping Strategy & Rules (Task 0.5)

To prevent redundant LLM invocations and token waste, scanner findings are deduplicated into **Finding Groups** using a deterministic multi-stage algorithm:

### 2.1 Grouping Algorithm
1. **Exact Fingerprint Match**: Findings sharing the exact non-empty `fingerprint` hash are merged into a single group.
2. **Exact Location Match (Fallback)**: If `fingerprint` is empty, findings sharing `rule_id + file + line` are merged.
3. **Near-Duplicate Match (Optional)**: Findings on the same `file` with the same `rule_id` whose line distance is within threshold (`abs(line1 - line2) <= 5`) are merged into a single group.
4. **ID & Location Preservation**: All original scanner finding IDs (`source_finding_ids`) and locations are preserved intact in the group output packet.
5. **Deterministic Sorting**: Groups are sorted deterministically by primary location (`file`, `line`) and `finding_id`.

---

## 3. Data Contracts & Schema (Task 0.4 & 0.6)

- **JSON Schema**: `schemas/security-analysis-record.schema.json` defines strict validation for output lines in `results/analysis/security-analysis.jsonl`.
- **LLM Provider Contract**: `week3/llm/base.py` specifies `AnalysisPacket`, `LLMResult`, and `LLMProvider` Protocol.
