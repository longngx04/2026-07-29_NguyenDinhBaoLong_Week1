from pathlib import Path
from week3.llm.fake import FakeLLM
from week3.llm.base import AnalysisPacket
from week3.validators import (
    read_jsonl,
    validate_provenance,
    validate_record_schema,
    write_jsonl_atomic,
)


def test_write_and_read_jsonl_atomic(tmp_path):
    output_file = tmp_path / "test.jsonl"
    records = [
        {"id": 1, "name": "alpha"},
        {"id": 2, "name": "beta"}
    ]
    write_jsonl_atomic(records, output_file)
    assert output_file.exists()
    
    loaded = read_jsonl(output_file)
    assert len(loaded) == 2
    assert loaded[0] == {"id": 1, "name": "alpha"}
    assert loaded[1] == {"id": 2, "name": "beta"}


def test_validate_record_schema_valid():
    schema_path = Path(__file__).parent.parent.parent / "schemas" / "security-analysis-record.schema.json"
    fake = FakeLLM()
    packet = AnalysisPacket(group_key="test-group")
    result = fake.analyze(packet)
    
    is_valid, err = validate_record_schema(result.parsed_response, schema_path)
    assert is_valid, f"Schema validation failed: {err}"


def test_validate_provenance_valid():
    fake = FakeLLM()
    packet = AnalysisPacket(
        group_key="group-1",
        finding_group={
            "source_finding_ids": ["f-01"],
            "locations": [{"file": "test.java", "line": 10}]
        },
        knowledge_hits=[{"path": "knowledge/cwe-89.md", "score": 10.0}]
    )
    result = fake.analyze(packet)
    rec = result.parsed_response
    
    is_valid, errors = validate_provenance(
        record_dict=rec,
        input_group_finding_ids=["f-01"],
        input_locations=[{"file": "test.java", "line": 10}],
        input_knowledge_paths=["knowledge/cwe-89.md"]
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
