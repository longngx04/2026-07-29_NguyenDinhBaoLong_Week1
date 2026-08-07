from pathlib import Path
import pytest
from project_sentinel.ingestion.input_loader import load_findings


def test_load_findings_valid():
    fixture_path = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "findings" / "valid.json"
    result = load_findings(fixture_path)
    assert result.count == 2
    assert len(result.findings) == 2
    assert result.findings[0].id == "opengrep-001"
    assert result.findings[0].location.file.endswith("VulnerableTaskHolder.java")
    assert result.findings[0].location.line == 69


def test_load_findings_missing_file():
    with pytest.raises(FileNotFoundError):
        load_findings("non_existent_file.json")


def test_load_findings_invalid_json(tmp_path):
    bad_json_file = tmp_path / "bad.json"
    bad_json_file.write_text("{invalid json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_findings(bad_json_file)


def test_load_findings_invalid_structure():
    fixture_path = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "findings" / "invalid.json"
    with pytest.raises(ValueError, match="Input JSON must contain a 'findings' array"):
        load_findings(fixture_path)


def test_load_findings_empty_id(tmp_path):
    f = tmp_path / "empty_id.json"
    f.write_text('{"count": 1, "findings": [{"id": "   ", "rule_id": "r1", "file": "a.py", "line": 1}]}', encoding="utf-8")
    with pytest.raises(ValueError, match="has empty id"):
        load_findings(f)


def test_load_findings_empty_rule_id(tmp_path):
    f = tmp_path / "empty_rule.json"
    f.write_text('{"count": 1, "findings": [{"id": "f1", "rule_id": "", "file": "a.py", "line": 1}]}', encoding="utf-8")
    with pytest.raises(ValueError, match="has empty rule_id"):
        load_findings(f)
