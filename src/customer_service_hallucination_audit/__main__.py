"""Command-line entry point for the hallucination audit project."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from contextlib import ExitStack
from importlib.resources import as_file, files
from pathlib import Path

from customer_service_hallucination_audit import __version__
from customer_service_hallucination_audit.detector import DETECTOR_ADAPTERS, select_detector
from customer_service_hallucination_audit.pipeline import run_audit

DEFAULT_DATA_PACKAGE = "customer_service_hallucination_audit.data"
DEFAULT_REPLIES_RESOURCE = "replies.json"
DEFAULT_GROUND_TRUTH_RESOURCE = "ground_truth.json"
DEFAULT_OUTPUT_DIR = Path("reports")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cs-hallucination-audit",
        description="Audit customer service replies for hallucination risk.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--replies",
        type=Path,
        default=None,
        help="Path to replies JSON input. Defaults to packaged data/replies.json.",
    )
    parser.add_argument(
        "--ground-truth",
        type=Path,
        default=None,
        help="Path to ground-truth labels JSON input. Defaults to packaged data/ground_truth.json.",
    )
    parser.add_argument(
        "--detector",
        default="deterministic",
        help=(
            "Detector adapter to run. "
            f"Expected one of: {', '.join(DETECTOR_ADAPTERS)}. "
            "Defaults to deterministic."
        ),
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
        with ExitStack() as resource_stack:
            replies_path = args.replies or _resolve_packaged_data_path(
                DEFAULT_REPLIES_RESOURCE,
                resource_stack,
            )
            labels_path = args.ground_truth or _resolve_packaged_data_path(
                DEFAULT_GROUND_TRUTH_RESOURCE,
                resource_stack,
            )
            detector = select_detector(args.detector)
            result = run_audit(
                replies_path=replies_path,
                labels_path=labels_path,
                output_dir=args.output_dir,
                detector=detector,
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


def _resolve_packaged_data_path(resource_name: str, resource_stack: ExitStack) -> Path:
    resource = files(DEFAULT_DATA_PACKAGE).joinpath(resource_name)
    return resource_stack.enter_context(as_file(resource))


if __name__ == "__main__":
    raise SystemExit(main())
