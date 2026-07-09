"""Command-line entry point for the hallucination audit project."""

from __future__ import annotations

import argparse

from customer_service_hallucination_audit import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cs-hallucination-audit",
        description="Audit customer service replies for hallucination risk.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main() -> None:
    build_parser().parse_args()


if __name__ == "__main__":
    main()
