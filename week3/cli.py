"""
CLI entry point for Week 3 Security Analysis Agent.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
from week3.config import AppConfig
from week3.pipeline import run_pipeline


def main(argv: Optional[List[str]] = None) -> int:
    """CLI main execution entry point."""
    parser = argparse.ArgumentParser(description="Week 3 Security Analysis Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # analyze sub-command
    analyze_parser = subparsers.add_parser("analyze", help="Run end-to-end security analysis pipeline")
    analyze_parser.add_argument("--input", type=Path, default=Path("results/normalized/findings.json"), help="Input normalized findings JSON")
    analyze_parser.add_argument("--output", type=Path, default=Path("results/analysis/security-analysis.jsonl"), help="Output security analysis JSONL")
    analyze_parser.add_argument("--summary", type=Path, default=Path("results/analysis/run-summary.json"), help="Output run summary JSON")
    analyze_parser.add_argument("--provider", type=str, choices=["fake", "openrouter"], default=None, help="LLM provider type")
    analyze_parser.add_argument("--target-root", type=Path, default=None, help="Target project root directory")
    analyze_parser.add_argument("--knowledge-dir", type=Path, default=Path("knowledge"), help="Knowledge base directory")

    args = parser.parse_args(argv)

    # If no subcommand given, default to analyze
    if args.command is None:
        args = parser.parse_args(["analyze"] + (argv if argv else []))

    try:
        config = AppConfig.from_env(
            input_findings_path=args.input,
            output_jsonl_path=args.output,
            summary_path=args.summary,
            provider_type=args.provider,
            knowledge_dir=args.knowledge_dir
        )

        summary = run_pipeline(config)
        print(f"Analysis complete: {summary['output_record_count']} records written to {config.output_jsonl_path}")
        print(f"Run summary written to {config.summary_path}")
        return 0
    except Exception as e:
        print(f"Pipeline execution error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
