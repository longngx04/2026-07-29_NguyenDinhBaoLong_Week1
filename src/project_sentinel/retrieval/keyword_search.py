"""Keyword search over the local Markdown knowledge base."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_KNOWLEDGE = Path("data/knowledge-base")
TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?", re.IGNORECASE)

# Expand common vuln aliases so queries like "SQL Injection" / "XSS" hit related docs.
SYNONYMS: dict[str, set[str]] = {
    "sql": {"sqli", "injection", "cwe-89", "cwe89", "a03"},
    "sqli": {"sql", "injection", "cwe-89", "cwe89"},
    "injection": {"sql", "sqli", "command", "cmdi", "a03"},
    "xss": {"cross", "site", "scripting", "cwe-79", "cwe79", "a03", "a07"},
    "cross": {"xss", "site", "scripting"},
    "scripting": {"xss", "cross", "site"},
    "command": {"cmdi", "rce", "exec", "cwe-78", "cwe78"},
    "cmdi": {"command", "injection", "exec", "cwe-78"},
    "ssrf": {"server", "side", "request", "forgery"},
    "xxe": {"xml", "external", "entity"},
    "csrf": {"cross", "site", "request", "forgery"},
    "idor": {"insecure", "direct", "object", "reference", "access"},
    "deserialization": {"insecure", "serialize", "cwe-502", "cwe502", "a08"},
}


@dataclass
class KnowledgeDoc:
    path: Path
    title: str
    tags: list[str]
    body: str


def tokenize(text: str) -> list[str]:
    return [tok.lower() for tok in TOKEN_RE.findall(text)]


def expand_query_tokens(tokens: list[str]) -> list[str]:
    expanded: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token not in seen:
            expanded.append(token)
            seen.add(token)
        for alias in SYNONYMS.get(token, ()):
            if alias not in seen:
                expanded.append(alias)
                seen.add(alias)
    return expanded


def parse_markdown(path: Path) -> KnowledgeDoc:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = path.stem.replace("-", " ").title()
    tags: list[str] = []
    body_start = 0

    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                body_start = i + 1
                break
            if lines[i].lower().startswith("title:"):
                title = lines[i].split(":", 1)[1].strip().strip("\"'")
            elif lines[i].lower().startswith("tags:"):
                raw = lines[i].split(":", 1)[1].strip()
                if raw.startswith("[") and raw.endswith("]"):
                    raw = raw[1:-1]
                tags = [t.strip().strip("\"'") for t in raw.split(",") if t.strip()]

    body_lines = lines[body_start:]
    for line in body_lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    body = "\n".join(body_lines).strip()
    return KnowledgeDoc(path=path, title=title, tags=tags, body=body)


def load_docs(knowledge_dir: Path = DEFAULT_KNOWLEDGE) -> list[KnowledgeDoc]:
    if not knowledge_dir.is_dir():
        raise FileNotFoundError(f"Knowledge directory not found: {knowledge_dir}")
    return [parse_markdown(path) for path in sorted(knowledge_dir.rglob("*.md"))]


def score_doc(query_tokens: list[str], original_tokens: list[str], doc: KnowledgeDoc) -> float:
    if not query_tokens:
        return 0.0
    title_tokens = set(tokenize(doc.title))
    tag_tokens = set(tokenize(" ".join(doc.tags)))
    body_tokens = set(tokenize(doc.body))
    joined_tags = " ".join(doc.tags).lower()
    searchable = f"{doc.title} {' '.join(doc.tags)} {doc.body}".lower()
    score = 0.0

    for token in query_tokens:
        weight = 1.0 if token in original_tokens else 0.35
        if token in title_tokens:
            score += 5.0 * weight
        if token in tag_tokens:
            score += 4.0 * weight
        if token in body_tokens:
            score += 1.0 * weight
        if token in joined_tags:
            score += 0.5 * weight

    # Phrase boost for multi-word original queries.
    phrase = " ".join(original_tokens)
    if len(original_tokens) >= 2 and phrase in searchable:
        score += 8.0

    return score


def snippet_for(query_tokens: list[str], body: str, width: int = 160) -> str:
    lower = body.lower()
    for token in query_tokens:
        idx = lower.find(token)
        if idx >= 0:
            start = max(0, idx - 40)
            end = min(len(body), idx + width)
            piece = body[start:end].replace("\n", " ").strip()
            if start > 0:
                piece = "…" + piece
            if end < len(body):
                piece = piece + "…"
            return piece
    compact = " ".join(body.split())
    return compact[:width] + ("…" if len(compact) > width else "")


def search(
    query: str,
    knowledge_dir: Path = DEFAULT_KNOWLEDGE,
    limit: int = 5,
) -> list[tuple[float, KnowledgeDoc, str]]:
    original_tokens = tokenize(query)
    query_tokens = expand_query_tokens(original_tokens)
    docs = load_docs(knowledge_dir)
    ranked: list[tuple[float, KnowledgeDoc, str]] = []
    for doc in docs:
        score = score_doc(query_tokens, original_tokens, doc)
        if score <= 0:
            continue
        ranked.append((score, doc, snippet_for(original_tokens or query_tokens, doc.body)))
    ranked.sort(key=lambda row: (-row[0], str(row[1].path)))
    return ranked[:limit]


def run_search(query: str, knowledge_dir: Path = DEFAULT_KNOWLEDGE, limit: int = 5) -> int:
    hits = search(query, knowledge_dir=knowledge_dir, limit=limit)
    if not hits:
        print(f"No knowledge matches for: {query!r}")
        return 1
    print(f"Query: {query!r} — {len(hits)} hit(s)\n")
    for i, (score, doc, snippet) in enumerate(hits, start=1):
        print(f"{i}. [{score:.1f}] {doc.title}")
        print(f"   path: {doc.path.as_posix()}")
        if doc.tags:
            print(f"   tags: {', '.join(doc.tags)}")
        print(f"   snippet: {snippet}")
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Keyword search over data/knowledge-base/.")
    parser.add_argument("query", nargs="+", help='Search query, e.g. "SQL Injection"')
    parser.add_argument("--knowledge", type=Path, default=DEFAULT_KNOWLEDGE)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)
    try:
        return run_search(" ".join(args.query), knowledge_dir=args.knowledge, limit=args.limit)
    except (FileNotFoundError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
