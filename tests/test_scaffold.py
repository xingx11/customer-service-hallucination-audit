import tomllib
from pathlib import Path

from customer_service_hallucination_audit import __version__
from customer_service_hallucination_audit.__main__ import build_parser

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "1.0.0"


def test_package_exposes_version() -> None:
    assert __version__ == EXPECTED_VERSION


def test_pyproject_uses_package_version_as_single_source() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["dynamic"] == ["version"]
    assert "version" not in pyproject["project"]
    assert pyproject["tool"]["setuptools"]["dynamic"]["version"] == {
        "attr": "customer_service_hallucination_audit.__version__"
    }


def test_cli_parser_has_expected_program_name() -> None:
    parser = build_parser()

    assert parser.prog == "cs-hallucination-audit"
