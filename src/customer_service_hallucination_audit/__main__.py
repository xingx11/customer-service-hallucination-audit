"""Command-line entry point for the hallucination audit project."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from customer_service_hallucination_audit import __version__
from customer_service_hallucination_audit.pipeline import run_audit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPLIES_PATH = PROJECT_ROOT / "data" / "replies.json"
DEFAULT_GROUND_TRUTH_PATH = PROJECT_ROOT / "data" / "ground_truth.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cs-hallucination-audit",
        description="Audit customer service replies for hallucination risk.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--replies",
        type=Path,
        default=DEFAULT_REPLIES_PATH,
        help="Path to replies JSON input. Defaults to data/replies.json.",
    )
    parser.add_argument(
        "--ground-truth",
        type=Path,
        default=DEFAULT_GROUND_TRUTH_PATH,
        help="Path to ground-truth labels JSON input. Defaults to data/ground_truth.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where report.md and report.json will be written.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        result = run_audit(
            replies_path=args.replies,
            labels_path=args.ground_truth,
            output_dir=args.output_dir,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Markdown report: {result.markdown_path}")
    print(f"JSON report: {result.json_path}")
    print(
        "Metrics: "
        f"total={result.metrics.total}, "
        f"precision={result.metrics.precision:.3f}, "
        f"recall={result.metrics.recall:.3f}, "
        f"f1={result.metrics.f1:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
