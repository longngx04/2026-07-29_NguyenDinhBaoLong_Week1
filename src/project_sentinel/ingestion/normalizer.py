"""Normalize OpenGrep native JSON into a shared finding schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .finding_schema import map_severity, short_rule_id, title_from_message
from project_sentinel.pathutil import canonicalize_source_path

DEFAULT_INPUT = Path("artifacts/raw/opengrep.json")
DEFAULT_OUTPUT = Path("artifacts/normalized/findings.json")


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
        "file_or_url": canonicalize_source_path(str(item.get("path") or "")),
        "line": start.get("line"),
        "title": title_from_message(message),
        "rule_id": short_rule_id(check_id),
        "cwe": metadata.get("cwe"),
        "owasp": metadata.get("owasp"),
        "message": message,
        "confidence": metadata.get("confidence"),
        "fingerprint": extra.get("fingerprint"),
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


def write_findings(findings: list[dict[str, Any]], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "opengrep",
        "count": len(findings),
        "findings": findings,
    }
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def run_normalize(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> list[dict[str, Any]]:
    if not input_path.is_file():
        raise FileNotFoundError(f"Raw report not found: {input_path}")
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    findings = normalize_report(raw)
    path = write_findings(findings, output_path)
    print(f"Normalized {len(findings)} findings -> {path}")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize OpenGrep JSON into a shared finding schema.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help=f"default: {DEFAULT_INPUT}")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=f"default: {DEFAULT_OUTPUT}")
    args = parser.parse_args(argv)
    try:
        run_normalize(input_path=args.input, output_path=args.output)
        return 0
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
