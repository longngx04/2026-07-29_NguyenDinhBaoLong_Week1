from pathlib import Path
from project_sentinel.analysis.analyzer import analyze_finding_group
from project_sentinel.config import AppConfig
from project_sentinel.analysis.grouping import group_findings
from project_sentinel.llm.fake import FakeLLM
from project_sentinel.models import NormalizedFinding, NormalizedLocation


def test_analyze_finding_group_fake_provider(tmp_path):
    rel_path = "benchmarks/targets/webgoat/src/Vulnerable.java"
    target_file = tmp_path / "benchmarks" / "targets" / "webgoat" / "src" / "Vulnerable.java"
    target_file.parent.mkdir(parents=True)
    target_file.write_text("public class Vulnerable { void exec() {} }\n", encoding="utf-8")

    f1 = NormalizedFinding(
        id="f-01",
        rule_id="java-command-execution",
        title="Potential command injection",
        severity="high",
        confidence="MEDIUM",
        location=NormalizedLocation(file=rel_path, line=1),
        cwe=["CWE-78"],
        owasp=["A03:2021-Injection"]
    )

    groups = group_findings([f1])
    assert len(groups) == 1

    config = AppConfig(
        project_root=tmp_path,
        target_root=tmp_path / "benchmarks" / "targets" / "webgoat",
        provider_type="fake",
        knowledge_dir=Path(__file__).parent.parent.parent.parent / "data" / "knowledge-base",
        schema_path=Path(__file__).parent.parent.parent.parent / "schemas" / "security-analysis-record.schema.json"
    )

    fake_llm = FakeLLM()
    analysis_res = analyze_finding_group(groups[0], config, provider=fake_llm)

    assert analysis_res.group_key == groups[0].group_key
    assert len(analysis_res.prompt_payload.prompt_sha256) == 64
    assert analysis_res.llm_result.error is None
    assert analysis_res.llm_result.parsed_response is not None
    assert analysis_res.llm_result.parsed_response["group_key"] == groups[0].group_key
    assert fake_llm.call_count == 1


def test_analyze_finding_group_retry(tmp_path):
    f1 = NormalizedFinding(
        id="f-02",
        rule_id="java-sql-statement-execution",
        title="Potential SQL injection",
        severity="high",
        confidence="MEDIUM",
        location=NormalizedLocation(file="app/db.py", line=10)
    )

    groups = group_findings([f1])
    config = AppConfig(
        project_root=tmp_path,
        provider_type="fake",
        max_retries=1
    )

    fake_retry_llm = FakeLLM(should_fail_first=True, max_retries=1)
    res = analyze_finding_group(groups[0], config, provider=fake_retry_llm)

    assert res.llm_result.error is None
    assert res.llm_result.parsed_response is not None
    assert fake_retry_llm.call_count == 2
