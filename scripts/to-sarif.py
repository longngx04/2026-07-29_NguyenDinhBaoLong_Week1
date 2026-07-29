#!/usr/bin/env python3
"""Convert OpenGrep native JSON to SARIF 2.1.0 for GitHub Code Scanning."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SEVERITY_MAP = {
    "ERROR": "error",
    "WARNING": "warning",
    "INFO": "note",
}

SECURITY_SEVERITY_MAP = {
    "ERROR": "8.0",
    "WARNING": "5.0",
    "INFO": "2.0",
}


def short_rule_id(check_id: str) -> str:
    return check_id.split(".")[-1] if "." in check_id else check_id


def convert(raw: dict) -> dict:
    tool_version = str(raw.get("version", "unknown"))
    results = raw.get("results", [])

    # Collect unique rules
    rules: dict[str, dict] = {}
    sarif_results: list[dict] = []

    for item in results:
        check_id = str(item.get("check_id", ""))
        rule_id = short_rule_id(check_id)
        extra = item.get("extra") or {}
        metadata = extra.get("metadata") or {}
        message = str(extra.get("message", check_id))
        severity = str(extra.get("severity", "INFO")).upper()
        cwe = metadata.get("cwe", "")
        owasp = metadata.get("owasp", "")
        path = str(item.get("path", ""))
        start = item.get("start") or {}
        end = item.get("end") or {}
        start_line = int(start.get("line", 1))
        start_col = int(start.get("col", 1))
        end_line = int(end.get("line", start_line))
        end_col = int(end.get("col", start_col + 1))

        # Register rule once
        if rule_id not in rules:
            tags = ["security"]
            if cwe:
                tags.append(cwe)
            if owasp:
                tags.append(owasp)
            rules[rule_id] = {
                "id": rule_id,
                "name": rule_id,
                "shortDescription": {"text": message[:100]},
                "fullDescription": {"text": message},
                "help": {
                    "text": message,
                    "markdown": (
                        f"**{rule_id}**\n\n{message}"
                        + (f"\n\n**CWE:** {cwe}" if cwe else "")
                        + (f"\n\n**OWASP:** {owasp}" if owasp else "")
                    ),
                },
                "properties": {
                    "tags": tags,
                    "precision": "medium",
                    "problem.severity": SEVERITY_MAP.get(severity, "note"),
                    "security-severity": SECURITY_SEVERITY_MAP.get(severity, "2.0"),
                },
            }

        sarif_results.append(
            {
                "ruleId": rule_id,
                "level": SEVERITY_MAP.get(severity, "note"),
                "message": {"text": message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": path,
                                "uriBaseId": "%SRCROOT%",
                            },
                            "region": {
                                "startLine": start_line,
                                "startColumn": start_col,
                                "endLine": end_line,
                                "endColumn": end_col,
                            },
                        }
                    }
                ],
            }
        )

    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "OpenGrep",
                        "version": tool_version,
                        "informationUri": "https://github.com/opengrep/opengrep",
                        "rules": list(rules.values()),
                    }
                },
                "results": sarif_results,
            }
        ],
    }


def main() -> int:
    raw_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/raw/opengrep.json")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("results/sarif/opengrep.sarif")

    if not raw_path.is_file():
        print(f"error: {raw_path} not found", file=sys.stderr)
        return 1

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    sarif = convert(raw)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sarif, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    n = len(sarif["runs"][0]["results"])
    n_rules = len(sarif["runs"][0]["tool"]["driver"]["rules"])
    print(f"SARIF written: {out_path}  ({n} results, {n_rules} rules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
