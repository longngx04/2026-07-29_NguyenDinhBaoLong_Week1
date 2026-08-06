from pathlib import Path
from week3.cli import main


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
