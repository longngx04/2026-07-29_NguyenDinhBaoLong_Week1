"""Keyword search over the local Markdown knowledge base."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_KNOWLEDGE = Path("knowledge")
TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?", re.IGNORECASE)


@dataclass
class KnowledgeDoc:
    path: Path
    title: str
    tags: list[str]
    body: str

    @property
    def searchable(self) -> str:
        return " ".join([self.title, " ".join(self.tags), self.body]).lower()


def tokenize(text: str) -> list[str]:
    return [tok.lower() for tok in TOKEN_RE.findall(text)]


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
    docs: list[KnowledgeDoc] = []
    for path in sorted(knowledge_dir.rglob("*.md")):
        docs.append(parse_markdown(path))
    return docs


def score_doc(query_tokens: list[str], doc: KnowledgeDoc) -> float:
    if not query_tokens:
        return 0.0
    title_tokens = set(tokenize(doc.title))
    tag_tokens = set(tokenize(" ".join(doc.tags)))
    body_tokens = set(tokenize(doc.body))
    score = 0.0
    for token in query_tokens:
        if token in title_tokens:
            score += 5.0
        if token in tag_tokens:
            score += 4.0
        if token in body_tokens:
            score += 1.0
        # Phrase-ish boost for multi-part tags like sql-injection
        joined_tags = " ".join(doc.tags).lower()
        if token in joined_tags or any(token in t for t in doc.tags):
            score += 0.5
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
    query_tokens = tokenize(query)
    docs = load_docs(knowledge_dir)
    ranked: list[tuple[float, KnowledgeDoc, str]] = []
    for doc in docs:
        score = score_doc(query_tokens, doc)
        if score <= 0:
            continue
        ranked.append((score, doc, snippet_for(query_tokens, doc.body)))
    ranked.sort(key=lambda row: (-row[0], str(row[1].path)))
    return ranked[:limit]


def run_search(query: str, knowledge_dir: Path = DEFAULT_KNOWLEDGE, limit: int = 5) -> int:
    hits = search(query, knowledge_dir=knowledge_dir, limit=limit)
    if not hits:
        print(f"No knowledge matches for: {query!r}")
        return 1
    print(f"Query: {query!r} — {len(hits)} hit(s)\n")
    for i, (score, doc, snippet) in enumerate(hits, start=1):
        rel = doc.path.as_posix()
        print(f"{i}. [{score:.1f}] {doc.title}")
        print(f"   path: {rel}")
        if doc.tags:
            print(f"   tags: {', '.join(doc.tags)}")
        print(f"   snippet: {snippet}")
        print()
    return 0
