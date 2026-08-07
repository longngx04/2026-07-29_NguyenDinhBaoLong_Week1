from project_sentinel.llm.base import AnalysisPacket
from project_sentinel.llm.fake import FakeLLM


def test_fake_llm_basic():
    fake = FakeLLM()
    packet = AnalysisPacket(
        group_key="group-1",
        finding_group={
            "source_finding_ids": ["f-01"],
            "locations": [{"file": "Main.java", "line": 15}],
            "cwe": ["CWE-78"],
            "owasp": ["A03:2021-Injection"]
        }
    )
    result = fake.analyze(packet)
    assert result.error is None
    assert result.parsed_response is not None
    assert result.parsed_response["group_key"] == "group-1"
    assert result.parsed_response["source_finding_ids"] == ["f-01"]
    assert result.model_name == "fake-llm"
    assert fake.call_count == 1


def test_fake_llm_retry_simulation():
    fake = FakeLLM(should_fail_first=True)
    packet = AnalysisPacket(group_key="group-retry")
    
    # First attempt fails
    r1 = fake.analyze(packet)
    assert r1.error is not None
    assert r1.parsed_response is None
    assert fake.call_count == 1
    
    # Second attempt succeeds
    r2 = fake.analyze(packet)
    assert r2.error is None
    assert r2.parsed_response is not None
    assert fake.call_count == 2
