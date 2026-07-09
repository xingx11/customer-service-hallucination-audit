from customer_service_hallucination_audit import __version__
from customer_service_hallucination_audit.__main__ import build_parser


def test_package_exposes_version() -> None:
    assert __version__ == "0.1.0"


def test_cli_parser_has_expected_program_name() -> None:
    parser = build_parser()

    assert parser.prog == "cs-hallucination-audit"
