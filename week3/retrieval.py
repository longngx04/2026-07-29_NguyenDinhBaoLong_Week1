"""
Knowledge retrieval adapter for Week 3 Security Analysis Agent.
Reuses week2.search keyword search engine to retrieve relevant knowledge documents.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from week2.search import search as week2_search


@dataclass
class RetrievalHit:
    """Structured knowledge retrieval hit."""
    path: str
    title: str
    score: float
    snippet: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert hit to dictionary payload for LLM analysis packet or output record."""
        return {
            "path": self.path,
            "title": self.title,
            "score": round(self.score, 2),
            "snippet": self.snippet
        }


def retrieve_knowledge(
    title: str,
    rule_id: str = "",
    cwe: Optional[List[str]] = None,
    owasp: Optional[List[str]] = None,
    knowledge_dir: Path = Path("knowledge"),
    top_k: int = 3,
    max_snippet_chars: int = 700
) -> List[RetrievalHit]:
    """Retrieve relevant knowledge hits for a finding group using week2.search keyword engine.
    
    Returns structured hits sorted by relevance score. Returns empty list if query is empty
    or knowledge_dir does not exist.
    """
    if not knowledge_dir.exists() or not knowledge_dir.is_dir():
        return []

    query_parts: List[str] = []
    
    if title and title.strip():
        query_parts.append(title.strip())
    if rule_id and rule_id.strip():
        query_parts.append(rule_id.strip())
    if cwe:
        query_parts.extend([str(c).strip() for c in cwe if str(c).strip()])
    if owasp:
        query_parts.extend([str(o).strip() for o in owasp if str(o).strip()])

    query = " ".join(query_parts).strip()
    if not query:
        return []

    try:
        raw_hits = week2_search(query=query, knowledge_dir=knowledge_dir, limit=top_k)
    except (FileNotFoundError, OSError, ValueError):
        return []

    hits: List[RetrievalHit] = []
    for score, doc, snippet in raw_hits:
        rel_path = doc.path.as_posix()
        clean_snippet = snippet if len(snippet) <= max_snippet_chars else snippet[:max_snippet_chars] + "..."
        hits.append(
            RetrievalHit(
                path=rel_path,
                title=doc.title,
                score=score,
                snippet=clean_snippet
            )
        )

    return hits
