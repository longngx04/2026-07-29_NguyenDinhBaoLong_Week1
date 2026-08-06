from pathlib import Path
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


def test_cli_exit_code_4_all_invalid_output(tmp_path):
    input_file = Path(__file__).parent.parent.parent / "fixtures" / "week3" / "valid-findings.json"
    output_jsonl = tmp_path / "output.jsonl"
    summary_file = tmp_path / "summary.json"

    fake_invalid = FakeLLM(inject_invalid_provenance=True)
    import week3.pipeline
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
