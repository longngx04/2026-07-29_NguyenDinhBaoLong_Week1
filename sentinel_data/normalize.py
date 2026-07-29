"""Normalize OpenGrep native JSON into a shared finding schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import map_severity, short_rule_id, title_from_message

DEFAULT_RAW = Path("results/raw/opengrep.json")
DEFAULT_OUT_DIR = Path("results/normalized")


def normalize_opengrep_result(item: dict[str, Any], index: int, tool_version: str) -> dict[str, Any]:
    extra = item.get("extra") or {}
    metadata = extra.get("metadata") or {}
    start = item.get("start") or {}
    check_id = str(item.get("check_id") or "")
    message = str(extra.get("message") or check_id)

    return {
        "id": f"opengrep-{index:03d}",
        "tool": "opengrep",
        "tool_version": tool_version,
        "severity": map_severity(extra.get("severity")),
        "file_or_url": str(item.get("path") or ""),
        "line": start.get("line"),
        "title": title_from_message(message),
        "rule_id": short_rule_id(check_id),
        "cwe": metadata.get("cwe"),
        "owasp": metadata.get("owasp"),
        "message": message,
        "confidence": metadata.get("confidence"),
        "raw_check_id": check_id,
    }


def normalize_report(raw: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(raw, dict):
        raise ValueError("OpenGrep report must be a JSON object")
    results = raw.get("results")
    if not isinstance(results, list):
        raise ValueError("OpenGrep report missing results array")
    version = str(raw.get("version") or "unknown")
    findings: list[dict[str, Any]] = []
    for i, item in enumerate(results, start=1):
        if not isinstance(item, dict):
            continue
        findings.append(normalize_opengrep_result(item, i, version))
    return findings


def write_findings(findings: list[dict[str, Any]], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "findings.json"
    jsonl_path = out_dir / "findings.jsonl"
    json_path.write_text(json.dumps(findings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for finding in findings:
            handle.write(json.dumps(finding, ensure_ascii=False) + "\n")
    return json_path, jsonl_path


def run_normalize(raw_path: Path = DEFAULT_RAW, out_dir: Path = DEFAULT_OUT_DIR) -> list[dict[str, Any]]:
    if not raw_path.is_file():
        raise FileNotFoundError(f"Raw report not found: {raw_path}")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    findings = normalize_report(raw)
    json_path, jsonl_path = write_findings(findings, out_dir)
    print(f"Normalized {len(findings)} findings")
    print(f"  JSON:  {json_path}")
    print(f"  JSONL: {jsonl_path}")
    return findings
