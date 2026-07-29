"""CLI entry: python -m sentinel_data normalize|search ..."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .normalize import DEFAULT_OUT_DIR, DEFAULT_RAW, run_normalize
from .search import DEFAULT_KNOWLEDGE, run_search


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinel_data",
        description="Normalize Week-1 OpenGrep findings and search the knowledge base.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    normalize = sub.add_parser("normalize", help="Normalize results/raw/opengrep.json")
    normalize.add_argument(
        "--raw",
        type=Path,
        default=DEFAULT_RAW,
        help=f"Path to OpenGrep JSON (default: {DEFAULT_RAW})",
    )
    normalize.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUT_DIR})",
    )

    search = sub.add_parser("search", help="Keyword search over knowledge/")
    search.add_argument("query", nargs="+", help="Search query, e.g. SQL Injection")
    search.add_argument(
        "--knowledge",
        type=Path,
        default=DEFAULT_KNOWLEDGE,
        help=f"Knowledge directory (default: {DEFAULT_KNOWLEDGE})",
    )
    search.add_argument("--limit", type=int, default=5, help="Max results (default: 5)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "normalize":
            run_normalize(raw_path=args.raw, out_dir=args.out_dir)
            return 0
        if args.command == "search":
            query = " ".join(args.query)
            return run_search(query, knowledge_dir=args.knowledge, limit=args.limit)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
