from __future__ import annotations

from pathlib import Path

import pytest

from customer_service_hallucination_audit import __version__
from customer_service_hallucination_audit.__main__ import build_parser, main

REPO_ROOT = Path(__file__).resolve().parents[1]
REPLIES_PATH = REPO_ROOT / "data" / "replies.json"
GROUND_TRUTH_PATH = REPO_ROOT / "data" / "ground_truth.json"
EXPECTED_VERSION = "0.3.0.dev0"


def test_cli_help_describes_input_and_output_options(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["--help"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "--replies" in captured.out
    assert "--ground-truth" in captured.out
    assert "--output-dir" in captured.out


def test_cli_parser_defers_default_input_resolution_to_runtime() -> None:
    args = build_parser().parse_args([])

    assert args.replies is None
    assert args.ground_truth is None
    assert args.output_dir == Path("reports")


def test_cli_version_reports_package_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert __version__ == EXPECTED_VERSION

    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["--version"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert captured.out.strip() == f"cs-hallucination-audit {EXPECTED_VERSION}"


def test_cli_runs_with_explicit_inputs_and_output_dir(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "--replies",
            str(REPLIES_PATH),
            "--ground-truth",
            str(GROUND_TRUTH_PATH),
            "--output-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Markdown report:" in captured.out
    assert "JSON report:" in captured.out
    assert (tmp_path / "report.md").exists()
    assert (tmp_path / "report.json").exists()


def test_cli_runs_with_packaged_default_inputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["--output-dir", str(tmp_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Metrics: total=" in captured.out
    assert "precision=" in captured.out
    assert "recall=" in captured.out
    assert "f1=" in captured.out
    assert (tmp_path / "report.md").exists()
    assert (tmp_path / "report.json").exists()


def test_cli_returns_nonzero_for_invalid_input_path(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "--replies",
            str(tmp_path / "missing-replies.json"),
            "--ground-truth",
            str(GROUND_TRUTH_PATH),
            "--output-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Cannot read JSON file" in captured.err
    assert not (tmp_path / "report.md").exists()
