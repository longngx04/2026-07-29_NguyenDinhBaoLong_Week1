from pathlib import Path
import week3.analyzer
from week3.cli import main
from week3.llm.fake import FakeLLM


def test_cli_analyze_mock(tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    output_jsonl = tmp_path / "output.jsonl"
    summary_file = tmp_path / "summary.json"

    argv = [
        "analyze",
        "--input", str(input_file),
        "--output", str(output_jsonl),
        "--summary", str(summary_file),
        "--provider", "fake"
    ]

    exit_code = main(argv)
    assert exit_code == 0
    assert output_jsonl.exists()
    assert summary_file.exists()


def test_cli_exit_code_2_nonexistent_input():
    argv = ["analyze", "--input", "/nonexistent_findings.json", "--provider", "fake"]
    exit_code = main(argv)
    assert exit_code == 2


def test_cli_exit_code_2_invalid_findings(tmp_path):
    invalid_file = tmp_path / "invalid-findings.json"
    invalid_file.write_text("{malformed json}", encoding="utf-8")
    output_jsonl = tmp_path / "output.jsonl"
    summary_file = tmp_path / "summary.json"

    argv = [
        "analyze",
        "--input", str(invalid_file),
        "--output", str(output_jsonl),
        "--summary", str(summary_file),
        "--provider", "fake"
    ]
    exit_code = main(argv)
    assert exit_code == 2
    assert not output_jsonl.exists()


def test_cli_exit_code_3_openrouter_missing_key(monkeypatch, tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("LLM_API_KEY", "")

    argv = [
        "analyze",
        "--input", str(input_file),
        "--output", str(tmp_path / "out.jsonl"),
        "--summary", str(tmp_path / "sum.json")
    ]
    exit_code = main(argv)
    assert exit_code == 3


def test_cli_exit_code_4_all_invalid_output(tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    output_jsonl = tmp_path / "output.jsonl"
    summary_file = tmp_path / "summary.json"

    fake_invalid = FakeLLM(inject_invalid_provenance=True)
    original_build_llm = week3.pipeline.build_llm
    week3.pipeline.build_llm = lambda cfg: fake_invalid

    argv = [
        "analyze",
        "--input", str(input_file),
        "--output", str(output_jsonl),
        "--summary", str(summary_file),
        "--provider", "fake"
    ]

    # Temporarily set VALIDATION_MAX_RETRIES env to 0
    import os
    os.environ["VALIDATION_MAX_RETRIES"] = "0"
    try:
        exit_code = main(argv)
        assert exit_code == 4
    finally:
        os.environ.pop("VALIDATION_MAX_RETRIES", None)
        week3.pipeline.build_llm = original_build_llm


def test_cli_validate_command_success(tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    output_jsonl = tmp_path / "output.jsonl"
    summary_file = tmp_path / "summary.json"

    # First run analyze to generate valid jsonl output
    assert main(["analyze", "--input", str(input_file), "--output", str(output_jsonl), "--summary", str(summary_file), "--provider", "fake"]) == 0

    # Then run validate command
    val_exit_code = main(["validate", "--input", str(output_jsonl)])
    assert val_exit_code == 0


def test_cli_target_root_wiring(tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    output_jsonl = tmp_path / "output.jsonl"
    summary_file = tmp_path / "summary.json"
    target_root = tmp_path / "custom_target_root"
    target_root.mkdir()

    captured_target_roots = []
    original_build_packet = week3.analyzer.build_analysis_packet

    def spy_build_packet(group, config, target_root=None):
        captured_target_roots.append(target_root or config.target_root)
        return original_build_packet(group, config, target_root=target_root)

    week3.analyzer.build_analysis_packet = spy_build_packet
    try:
        argv = [
            "analyze",
            "--input", str(input_file),
            "--output", str(output_jsonl),
            "--summary", str(summary_file),
            "--provider", "fake",
            "--target-root", str(target_root)
        ]
        exit_code = main(argv)
        assert exit_code == 0
        assert len(captured_target_roots) > 0
        assert captured_target_roots[0] == target_root
    finally:
        week3.analyzer.build_analysis_packet = original_build_packet
