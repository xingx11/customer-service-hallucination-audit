from __future__ import annotations

from pathlib import Path

from customer_service_hallucination_audit.pipeline import run_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
REPLIES_PATH = REPO_ROOT / "data" / "replies.json"
GROUND_TRUTH_PATH = REPO_ROOT / "data" / "ground_truth.json"
REPORTS_DIR = REPO_ROOT / "docs" / "reports"


def test_committed_stage_1_reports_match_pipeline_output(tmp_path: Path) -> None:
    result = run_audit(
        replies_path=REPLIES_PATH,
        labels_path=GROUND_TRUTH_PATH,
        output_dir=tmp_path,
        markdown_report_name="stage-1-report.md",
        json_report_name="stage-1-report.json",
    )

    committed_markdown = REPORTS_DIR / "stage-1-report.md"
    committed_json = REPORTS_DIR / "stage-1-report.json"

    assert committed_markdown.read_text(encoding="utf-8") == result.markdown_path.read_text(
        encoding="utf-8"
    )
    assert committed_json.read_text(encoding="utf-8") == result.json_path.read_text(
        encoding="utf-8"
    )
