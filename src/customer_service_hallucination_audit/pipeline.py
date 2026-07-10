"""End-to-end orchestration for the offline hallucination audit pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from customer_service_hallucination_audit.detector import detect_replies
from customer_service_hallucination_audit.io import load_audit_dataset
from customer_service_hallucination_audit.metrics import (
    analyze_errors,
    calculate_metrics,
    calculate_type_metrics,
)
from customer_service_hallucination_audit.models import (
    DetectionResult,
    ErrorCase,
    MetricsSummary,
    TypeMetricsSummary,
)
from customer_service_hallucination_audit.reporting import (
    render_json_report,
    render_markdown_report,
)

DEFAULT_MARKDOWN_REPORT_NAME = "report.md"
DEFAULT_JSON_REPORT_NAME = "report.json"


@dataclass(frozen=True)
class AuditRunResult:
    """Artifacts and summary data produced by one audit pipeline run."""

    results: tuple[DetectionResult, ...]
    metrics: MetricsSummary
    type_metrics: tuple[TypeMetricsSummary, ...]
    error_cases: tuple[ErrorCase, ...]
    markdown_path: Path
    json_path: Path


def run_audit(
    *,
    replies_path: Path,
    labels_path: Path,
    output_dir: Path,
    markdown_report_name: str = DEFAULT_MARKDOWN_REPORT_NAME,
    json_report_name: str = DEFAULT_JSON_REPORT_NAME,
) -> AuditRunResult:
    """Run detection, evaluation, and report rendering for one dataset."""

    dataset = load_audit_dataset(replies_path, labels_path)
    results = detect_replies(dataset.replies)
    metrics = calculate_metrics(results, dataset.labels)
    type_metrics = calculate_type_metrics(results, dataset.labels)
    error_cases = analyze_errors(results, dataset.labels)

    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / markdown_report_name
    json_path = output_dir / json_report_name
    markdown_path.write_text(
        render_markdown_report(results, metrics, type_metrics, error_cases),
        encoding="utf-8",
    )
    json_path.write_text(
        render_json_report(results, metrics, type_metrics, error_cases),
        encoding="utf-8",
    )

    return AuditRunResult(
        results=results,
        metrics=metrics,
        type_metrics=type_metrics,
        error_cases=error_cases,
        markdown_path=markdown_path,
        json_path=json_path,
    )


__all__ = [
    "DEFAULT_JSON_REPORT_NAME",
    "DEFAULT_MARKDOWN_REPORT_NAME",
    "AuditRunResult",
    "run_audit",
]
