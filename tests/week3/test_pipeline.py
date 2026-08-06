import json
from pathlib import Path
from week3.config import AppConfig
from week3.llm.base import AnalysisPacket, LLMResult
from week3.llm.fake import FakeLLM
from week3.pipeline import run_pipeline
from week3.validators import read_jsonl


def test_pipeline_valid_findings_fake_llm(tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    output_jsonl = tmp_path / "security-analysis.jsonl"
    summary_file = tmp_path / "run-summary.json"

    config = AppConfig(
        project_root=tmp_path,
        input_findings_path=input_file,
        output_jsonl_path=output_jsonl,
        summary_path=summary_file,
        provider_type="fake",
        knowledge_dir=Path(__file__).parent.parent.parent / "knowledge",
        schema_path=Path(__file__).parent.parent.parent / "schemas" / "security-analysis-record.schema.json"
    )

    summary = run_pipeline(config)

    assert summary["schema_version"] == "1.0"
    assert summary["input_finding_count"] == 2
    assert summary["group_count"] == 2
    assert summary["output_record_count"] == 2
    assert summary["llm_call_count"] >= 2
    assert summary["invalid_output_count"] == 0

    assert output_jsonl.exists()
    records = read_jsonl(output_jsonl)
    assert len(records) == 2
    assert records[0]["schema_version"] == "1.0"

    assert summary_file.exists()
    summary_data = json.loads(summary_file.read_text(encoding="utf-8"))
    assert summary_data["output_record_count"] == 2


def test_pipeline_hallucinated_output_retry(tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    output_jsonl = tmp_path / "security-analysis.jsonl"
    summary_file = tmp_path / "run-summary.json"

    config = AppConfig(
        project_root=tmp_path,
        input_findings_path=input_file,
        output_jsonl_path=output_jsonl,
        summary_path=summary_file,
        provider_type="fake",
        validation_max_retries=0,
        knowledge_dir=Path(__file__).parent.parent.parent / "knowledge",
        schema_path=Path(__file__).parent.parent.parent / "schemas" / "security-analysis-record.schema.json"
    )

    # Force FakeLLM to return hallucinated source_finding_ids
    fake_hallucinated_llm = FakeLLM(
        custom_response={
            "schema_version": "1.0",
            "analysis_id": "analysis-123",
            "group_key": "group-e85d45d3e0",
            "source_finding_ids": ["hallucinated-finding-999"],
            "title": "Hallucinated Title",
            "severity": "high",
            "scanner_severities": ["high"],
            "confidence": "high",
            "confidence_rationale": "Test",
            "locations": [{"file": "targets/webgoat/src/Vulnerable.java", "line": 10}],
            "cwe": [],
            "owasp": [],
            "evidence": [],
            "explanation": "Test",
            "preconditions": [],
            "verification_steps": [],
            "remediation": [],
            "knowledge_refs": [],
            "limitations": []
        }
    )

    import week3.pipeline
    monkeypatch_llm = lambda cfg: fake_hallucinated_llm

    original_build_llm = week3.pipeline.build_llm
    week3.pipeline.build_llm = monkeypatch_llm
    try:
        summary = run_pipeline(config)
        assert summary["output_record_count"] == 0
        assert summary["invalid_output_count"] == 2
    finally:
        week3.pipeline.build_llm = original_build_llm


def test_pipeline_provenance_canary_invalid_flag(tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    output_jsonl = tmp_path / "security-analysis.jsonl"
    summary_file = tmp_path / "run-summary.json"

    config = AppConfig(
        project_root=tmp_path,
        input_findings_path=input_file,
        output_jsonl_path=output_jsonl,
        summary_path=summary_file,
        provider_type="fake",
        validation_max_retries=0,
        knowledge_dir=Path(__file__).parent.parent.parent / "knowledge",
        schema_path=Path(__file__).parent.parent.parent / "schemas" / "security-analysis-record.schema.json"
    )

    fake_canary = FakeLLM(inject_invalid_provenance=True)
    import week3.pipeline
    original_build_llm = week3.pipeline.build_llm
    week3.pipeline.build_llm = lambda cfg: fake_canary
    try:
        summary = run_pipeline(config)
        assert summary["output_record_count"] == 0
        assert summary["invalid_output_count"] >= 1
    finally:
        week3.pipeline.build_llm = original_build_llm


def test_pipeline_validation_retry_success(tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    output_jsonl = tmp_path / "security-analysis.jsonl"
    summary_file = tmp_path / "run-summary.json"

    config = AppConfig(
        project_root=tmp_path,
        input_findings_path=input_file,
        output_jsonl_path=output_jsonl,
        summary_path=summary_file,
        provider_type="fake",
        validation_max_retries=1,
        knowledge_dir=Path(__file__).parent.parent.parent / "knowledge",
        schema_path=Path(__file__).parent.parent.parent / "schemas" / "security-analysis-record.schema.json"
    )

    class FlakyValidationLLM:
        def __init__(self):
            self.calls = 0
            self.fake_invalid = FakeLLM(inject_invalid_provenance=True)
            self.fake_valid = FakeLLM()

        def analyze(self, packet: AnalysisPacket, system_prompt=None) -> LLMResult:
            self.calls += 1
            if system_prompt and "System Note: Your previous output failed validation" in system_prompt:
                return self.fake_valid.analyze(packet, system_prompt=system_prompt)
            return self.fake_invalid.analyze(packet, system_prompt=system_prompt)

    import week3.pipeline
    flaky_llm = FlakyValidationLLM()
    original_build_llm = week3.pipeline.build_llm
    week3.pipeline.build_llm = lambda cfg: flaky_llm
    try:
        summary = run_pipeline(config)
        assert summary["retry_count"] >= 1
        assert summary["output_record_count"] == 2
        assert summary["invalid_output_count"] == 0
    finally:
        week3.pipeline.build_llm = original_build_llm
