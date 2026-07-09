from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

import pytest

from customer_service_hallucination_audit.__main__ import build_parser, main
from customer_service_hallucination_audit.pipeline import run_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
REPLIES_PATH = REPO_ROOT / "data" / "replies.json"
GROUND_TRUTH_PATH = REPO_ROOT / "data" / "ground_truth.json"


def test_packaged_default_dataset_matches_source_data() -> None:
    package_data = files("customer_service_hallucination_audit").joinpath("data")

    assert json.loads(
        package_data.joinpath("replies.json").read_text(encoding="utf-8")
    ) == json.loads(REPLIES_PATH.read_text(encoding="utf-8"))
    assert json.loads(
        package_data.joinpath("ground_truth.json").read_text(encoding="utf-8")
    ) == json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))


def test_cli_parser_defers_default_input_resolution_to_runtime() -> None:
    args = build_parser().parse_args([])

    assert args.replies is None
    assert args.ground_truth is None
    assert args.output_dir == Path("reports")


def test_run_audit_writes_markdown_and_json_reports(tmp_path: Path) -> None:
    result = run_audit(
        replies_path=REPLIES_PATH,
        labels_path=GROUND_TRUTH_PATH,
        output_dir=tmp_path,
    )

    assert result.markdown_path == tmp_path / "report.md"
    assert result.json_path == tmp_path / "report.json"
    assert result.metrics.total == 20
    assert len(result.results) == 20
    assert result.markdown_path.read_text(encoding="utf-8").startswith("# 客服回复幻觉检测报告\n")

    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    assert payload["metrics"]["total"] == 20
    assert payload["results"][0]["case_id"] == "h01"


def test_cli_runs_default_pipeline_with_explicit_output_dir(
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
    assert "report.md" in captured.out
    assert (tmp_path / "report.md").exists()
    assert (tmp_path / "report.json").exists()


def test_cli_runs_with_packaged_default_inputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["--output-dir", str(tmp_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Metrics: total=20, precision=1.000, recall=1.000, f1=1.000" in captured.out
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


def test_default_reports_directory_is_git_ignored() -> None:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "reports/" in gitignore.splitlines()
