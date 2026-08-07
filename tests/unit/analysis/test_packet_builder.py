from pathlib import Path
from project_sentinel.config import AppConfig
from project_sentinel.analysis.grouping import group_findings
from project_sentinel.models import NormalizedFinding, NormalizedLocation
from project_sentinel.analysis.packet_builder import build_analysis_packet


def test_build_analysis_packet(tmp_path):
    # Setup test file
    target_dir = tmp_path / "benchmarks" / "targets" / "webgoat" / "src"
    target_dir.mkdir(parents=True)
    src_file = target_dir / "Test.java"
    src_file.write_text("package test;\npublic class Test {\n  void run() { execute(); }\n}\n", encoding="utf-8")

    rel_path = "benchmarks/targets/webgoat/src/Test.java"

    f1 = NormalizedFinding(
        id="f1",
        rule_id="java-sql-statement-execution",
        title="Potential SQL injection",
        severity="high",
        confidence="MEDIUM",
        location=NormalizedLocation(file=rel_path, line=3),
        cwe=["CWE-89"],
        owasp=["A03:2021-Injection"]
    )
    f2 = NormalizedFinding(
        id="f2",
        rule_id="java-sql-statement-execution",
        title="Potential SQL injection",
        severity="high",
        confidence="MEDIUM",
        location=NormalizedLocation(file=rel_path, line=3),
        cwe=["CWE-89"],
        owasp=["A03:2021-Injection"]
    )

    groups = group_findings([f1, f2])
    assert len(groups) == 1

    config = AppConfig(
        project_root=tmp_path,
        knowledge_dir=Path(__file__).parent.parent.parent.parent / "data" / "knowledge-base",
        schema_path=Path(__file__).parent.parent.parent.parent / "schemas" / "security-analysis-record.schema.json"
    )

    packet = build_analysis_packet(
        group=groups[0],
        config=config,
        project_root=tmp_path,
        target_root=tmp_path / "benchmarks" / "targets" / "webgoat"
    )

    assert packet.group_key == groups[0].group_key
    assert packet.finding_group["source_finding_ids"] == ["f1", "f2"]
    assert len(packet.source_evidence) == 1
    assert packet.source_evidence[0]["path"] == rel_path
    assert "execute()" in packet.source_evidence[0]["content"]
    assert len(packet.knowledge_hits) > 0
    assert packet.output_schema.get("title") == "SecurityAnalysisRecord"


def test_build_analysis_packet_with_limitations(tmp_path):
    f = NormalizedFinding(
        id="f-missing",
        rule_id="java-sql-injection",
        title="Missing file test",
        severity="medium",
        confidence="LOW",
        location=NormalizedLocation(file="missing.java", line=1)
    )
    groups = group_findings([f])
    config = AppConfig(project_root=tmp_path)
    packet = build_analysis_packet(groups[0], config)

    assert "input_limitations" in packet.finding_group
    assert len(packet.finding_group["input_limitations"]) == 1
    assert "missing.java" in packet.finding_group["input_limitations"][0]
