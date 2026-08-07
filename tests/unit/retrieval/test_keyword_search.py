from pathlib import Path
from project_sentinel.retrieval.knowledge_retriever import retrieve_knowledge


def test_retrieve_knowledge_sqli():
    knowledge_dir = Path(__file__).parent.parent.parent.parent / "data" / "knowledge-base"
    hits = retrieve_knowledge(
        title="Potential SQL injection",
        rule_id="java-sql-statement-execution",
        cwe=["CWE-89"],
        owasp=["A03:2021-Injection"],
        knowledge_dir=knowledge_dir,
        top_k=3
    )

    assert len(hits) > 0
    paths = [h.path for h in hits]
    # Check SQL injection example or OWASP doc is retrieved
    assert any("sql-injection" in p or "owasp-top10" in p for p in paths)
    assert hits[0].score > 0.0
    assert hits[0].snippet != ""


def test_retrieve_knowledge_deserialization():
    knowledge_dir = Path(__file__).parent.parent.parent.parent / "data" / "knowledge-base"
    hits = retrieve_knowledge(
        title="Insecure Deserialization",
        rule_id="java-unsafe-deserialization",
        cwe=["CWE-502"],
        owasp=["A08:2021-Software and Data Integrity Failures"],
        knowledge_dir=knowledge_dir,
        top_k=3
    )

    assert len(hits) > 0
    paths = [h.path for h in hits]
    assert any("deserialization" in p or "cwe-502" in p or "owasp" in p for p in paths)


def test_retrieve_knowledge_empty_query():
    knowledge_dir = Path(__file__).parent.parent.parent.parent / "data" / "knowledge-base"
    hits = retrieve_knowledge(
        title="",
        rule_id="",
        cwe=[],
        owasp=[],
        knowledge_dir=knowledge_dir
    )
    assert hits == []


def test_retrieve_knowledge_missing_dir(tmp_path):
    missing_dir = tmp_path / "non_existent_kb"
    hits = retrieve_knowledge(
        title="SQL Injection",
        knowledge_dir=missing_dir
    )
    assert hits == []
