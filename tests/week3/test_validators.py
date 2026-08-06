from pathlib import Path
from week3.llm.base import AnalysisPacket
from week3.llm.fake import FakeLLM
from week3.validators import read_jsonl, validate_provenance, validate_record_schema, write_jsonl_atomic


def test_write_and_read_jsonl_atomic(tmp_path):
    records = [
        {"id": "1", "data": "hello"},
        {"id": "2", "data": "world"}
    ]
    out_file = tmp_path / "test.jsonl"
    write_jsonl_atomic(records, out_file)
    
    assert out_file.exists()
    loaded = read_jsonl(out_file)
    assert len(loaded) == 2
    assert loaded[0]["data"] == "hello"


def test_validate_record_schema_valid():
    schema_file = Path(__file__).parent.parent.parent / "schemas" / "security-analysis-record.schema.json"
    fake = FakeLLM()
    packet = AnalysisPacket(group_key="group-1")
    result = fake.analyze(packet)
    rec = result.parsed_response
    
    is_valid, error = validate_record_schema(rec, schema_file)
    assert is_valid, f"Schema validation failed: {error}"


def test_validate_provenance_valid():
    fake = FakeLLM()
    packet = AnalysisPacket(
        group_key="group-1",
        finding_group={
            "source_finding_ids": ["f-01"],
            "locations": [{"file": "test.java", "line": 10}]
        },
        knowledge_hits=[{"path": "knowledge/cwe-89.md"}]
    )
    result = fake.analyze(packet)
    rec = result.parsed_response
    
    is_valid, errors = validate_provenance(
        record_dict=rec,
        input_group_finding_ids=["f-01"],
        input_locations=[{"file": "test.java", "line": 10}],
        input_knowledge_paths=["knowledge/cwe-89.md"],
        input_cwes=["CWE-89"],
        input_owasps=["A03:2021-Injection"]
    )
    assert is_valid, f"Provenance validation failed: {errors}"


def test_validate_provenance_hallucinated():
    fake = FakeLLM(inject_invalid_provenance=True)
    packet = AnalysisPacket(
        group_key="group-1",
        finding_group={
            "source_finding_ids": ["f-01"],
            "locations": [{"file": "test.java", "line": 10}]
        },
        knowledge_hits=[]
    )
    result = fake.analyze(packet)
    rec = result.parsed_response
    
    is_valid, errors = validate_provenance(
        record_dict=rec,
        input_group_finding_ids=["f-01"],
        input_locations=[{"file": "test.java", "line": 10}],
        input_knowledge_paths=[]
    )
    assert not is_valid
    assert any("fake-hallucinated-id-999" in e for e in errors)
    assert any("invented/path/Fake.java" in e for e in errors)


def test_validate_provenance_rejects_invented_when_input_empty():
    rec = {
        "source_finding_ids": ["f1"],
        "locations": [{"file": "a.java", "line": 1}],
        "cwe": ["CWE-999"],
        "owasp": [],
        "evidence": [],
        "knowledge_refs": []
    }
    ok, errs = validate_provenance(
        rec,
        ["f1"],
        [{"file": "a.java", "line": 1}],
        [],
        input_cwes=[],
        input_owasps=[],
        input_source_evidence=[]
    )
    assert not ok
    assert any("CWE" in e for e in errs)
