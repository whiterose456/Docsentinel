"""Command-line interface for Docsentinel."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .demo import run_demo
from .verifier import verify_payload


def main() -> int:
    parser = argparse.ArgumentParser(prog="docsentinel", description="Evidence-first citation verifier")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="run the built-in deterministic demonstration")
    verify_parser = subparsers.add_parser("verify", help="verify a structured answer JSON file")
    verify_parser.add_argument("--input", required=True, help="path to input JSON")
    args = parser.parse_args()

    try:
        if args.command == "demo":
            report = run_demo()
        else:
            with Path(args.input).open("r", encoding="utf-8") as handle:
                report = verify_payload(json.load(handle))
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"docsentinel: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
