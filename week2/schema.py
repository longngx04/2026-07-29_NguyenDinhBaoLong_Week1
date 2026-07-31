"""Shared schema helpers for normalized findings."""

from __future__ import annotations

SEVERITY_MAP = {
    "ERROR": "high",
    "WARNING": "medium",
    "INFO": "low",
    "INVENTORY": "info",
}


def map_severity(opengrep_severity: str | None) -> str:
    if not opengrep_severity:
        return "low"
    return SEVERITY_MAP.get(str(opengrep_severity).upper(), "low")


def short_rule_id(check_id: str) -> str:
    """rules.opengrep.java-sql-statement-execution -> java-sql-statement-execution"""
    parts = check_id.split(".")
    return parts[-1] if parts else check_id


def title_from_message(message: str, limit: int = 80) -> str:
    text = " ".join(message.strip().split())
    if not text:
        return "Untitled finding"
    # Prefer the clause before the first colon as a short title.
    head = text.split(":", 1)[0].strip()
    candidate = head if head else text
    if len(candidate) <= limit:
        return candidate
    return candidate[: limit - 1].rstrip() + "…"
