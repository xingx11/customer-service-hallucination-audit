"""Stable Markdown and JSON report rendering for audit results."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TypedDict

from customer_service_hallucination_audit.detector import DETECTION_RULES
from customer_service_hallucination_audit.metrics import select_error_cases
from customer_service_hallucination_audit.models import (
    DetectionResult,
    ErrorCase,
    ErrorType,
    GroundTruthLabel,
    HallucinationType,
    MetricsSummary,
    RuleMetadata,
    RuleRiskLevel,
    TypeMetricsSummary,
)

LIMITATIONS: tuple[str, ...] = (
    "默认交付报告仅覆盖20条固定样本，样本规模不足以代表所有客服场景。",
    "当前报告基于离线确定性规则，无法覆盖所有客服回复表达变体或规则外风险。",
    "人工真值只用于评估和错误分析，不参与检测器预测。",
    "高风险案例按漏检和安全误导相关错误保守筛选，后续可结合业务风险继续细化。",
)

HIGH_RISK_RATIONALE: tuple[str, ...] = (
    "纳入所有漏检案例。",
    "纳入人工标注或预测类型为安全误导的错误案例。",
    "输出按样本 ID 稳定排序，便于复现和 diff 审阅。",
)


class MetricsPayload(TypedDict):
    total: int
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    precision: float
    recall: float
    f1: float
    accuracy: float


class TypeMetricsPayload(TypedDict):
    hallucination_type: HallucinationType
    label_count: int
    predicted_count: int
    true_positive_count: int
    mismatch_count: int


class ResultPayload(TypedDict):
    case_id: str
    is_hallucination: bool
    hallucination_type: HallucinationType | None
    reasons: list[str]
    rule_ids: list[str]


class RuleHitPayload(TypedDict):
    rule_id: str
    hallucination_type: HallucinationType
    risk_level: RuleRiskLevel
    description: str
    trigger_intent: str
    hit_count: int
    case_ids: list[str]


class LabelPayload(TypedDict):
    case_id: str
    is_hallucination: bool
    hallucination_type: HallucinationType | None
    detail: str


class ErrorPayload(TypedDict):
    case_id: str
    error_type: ErrorType
    expected: LabelPayload
    predicted: ResultPayload


class ReportPayload(TypedDict):
    metrics: MetricsPayload
    type_metrics: list[TypeMetricsPayload]
    results: list[ResultPayload]
    rule_hit_summary: list[RuleHitPayload]
    false_positives: list[ErrorPayload]
    false_negatives: list[ErrorPayload]
    type_mismatches: list[ErrorPayload]
    high_risk_rationale: list[str]
    high_risk_cases: list[ErrorPayload]
    limitations: list[str]


@dataclass(frozen=True)
class ReportSections:
    results: tuple[DetectionResult, ...]
    type_metrics: tuple[TypeMetricsSummary, ...]
    rule_hit_summary: tuple[RuleHitSummary, ...]
    false_positives: tuple[ErrorCase, ...]
    false_negatives: tuple[ErrorCase, ...]
    type_mismatches: tuple[ErrorCase, ...]
    high_risk_cases: tuple[ErrorCase, ...]


@dataclass(frozen=True)
class RuleHitSummary:
    metadata: RuleMetadata
    case_ids: tuple[str, ...]

    @property
    def hit_count(self) -> int:
        return len(self.case_ids)


def build_report_payload(
    results: Iterable[DetectionResult],
    metrics: MetricsSummary,
    type_metrics: Iterable[TypeMetricsSummary],
    error_cases: Iterable[ErrorCase],
) -> ReportPayload:
    """Build the machine-readable report structure with stable ordering."""

    sections = _prepare_report_sections(results, type_metrics, error_cases)

    return {
        "metrics": _metrics_to_payload(metrics),
        "type_metrics": [
            _type_metrics_to_payload(type_metric) for type_metric in sections.type_metrics
        ],
        "results": [_result_to_payload(result) for result in sections.results],
        "rule_hit_summary": [
            _rule_hit_summary_to_payload(summary) for summary in sections.rule_hit_summary
        ],
        "false_positives": [
            _error_to_payload(error_case) for error_case in sections.false_positives
        ],
        "false_negatives": [
            _error_to_payload(error_case) for error_case in sections.false_negatives
        ],
        "type_mismatches": [
            _error_to_payload(error_case) for error_case in sections.type_mismatches
        ],
        "high_risk_rationale": list(HIGH_RISK_RATIONALE),
        "high_risk_cases": [
            _error_to_payload(error_case) for error_case in sections.high_risk_cases
        ],
        "limitations": list(LIMITATIONS),
    }


def render_json_report(
    results: Iterable[DetectionResult],
    metrics: MetricsSummary,
    type_metrics: Iterable[TypeMetricsSummary],
    error_cases: Iterable[ErrorCase],
) -> str:
    """Render a deterministic UTF-8 JSON report string."""

    return (
        json.dumps(
            build_report_payload(results, metrics, type_metrics, error_cases),
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


def render_markdown_report(
    results: Iterable[DetectionResult],
    metrics: MetricsSummary,
    type_metrics: Iterable[TypeMetricsSummary],
    error_cases: Iterable[ErrorCase],
) -> str:
    """Render a human-readable Markdown report with stable sections."""

    sections = _prepare_report_sections(results, type_metrics, error_cases)

    lines: list[str] = [
        "# 客服回复幻觉检测报告",
        "",
        "## 总体指标",
        "",
        "| 指标 | 值 |",
        "| --- | --- |",
        f"| 样本数 | {metrics.total} |",
        f"| True Positive | {metrics.true_positive} |",
        f"| False Positive | {metrics.false_positive} |",
        f"| True Negative | {metrics.true_negative} |",
        f"| False Negative | {metrics.false_negative} |",
        f"| Precision | {_format_rate(metrics.precision)} |",
        f"| Recall | {_format_rate(metrics.recall)} |",
        f"| F1 | {_format_rate(metrics.f1)} |",
        f"| Accuracy | {_format_rate(metrics.accuracy)} |",
        "",
        "## 类型表现",
        "",
        *_render_type_metrics(sections.type_metrics),
        "",
        "## 分类结果",
        "",
        "| 样本 ID | 是否幻觉 | 幻觉类型 | 触发规则 | 原因 |",
        "| --- | --- | --- | --- | --- |",
    ]

    lines.extend(_render_result_row(result) for result in sections.results)
    lines.extend(
        [
            "",
            "## 规则命中摘要",
            "",
            *_render_rule_hit_summary(sections.rule_hit_summary),
            "",
            "## 漏检",
            "",
            *_render_error_lines(sections.false_negatives, _format_false_negative),
            "",
            "## 误报",
            "",
            *_render_error_lines(sections.false_positives, _format_false_positive),
            "",
            "## 类型错误",
            "",
            *_render_error_lines(sections.type_mismatches, _format_type_mismatch),
            "",
            "## 高风险案例",
            "",
            "筛选与排序依据：",
            "",
            *(f"- {rationale}" for rationale in HIGH_RISK_RATIONALE),
            "",
            *_render_error_lines(sections.high_risk_cases, _format_high_risk_case),
            "",
            "## 局限性",
            "",
            *(f"- {limitation}" for limitation in LIMITATIONS),
        ]
    )
    return "\n".join(lines) + "\n"


def _prepare_report_sections(
    results: Iterable[DetectionResult],
    type_metrics: Iterable[TypeMetricsSummary],
    error_cases: Iterable[ErrorCase],
) -> ReportSections:
    sorted_results = tuple(sorted(results, key=lambda result: result.case_id))
    type_metrics_tuple = tuple(type_metrics)
    sorted_errors = tuple(sorted(error_cases, key=lambda error_case: error_case.case_id))
    return ReportSections(
        results=sorted_results,
        type_metrics=type_metrics_tuple,
        rule_hit_summary=_summarize_rule_hits(sorted_results),
        false_positives=select_error_cases(sorted_errors, "false_positive"),
        false_negatives=select_error_cases(sorted_errors, "false_negative"),
        type_mismatches=select_error_cases(sorted_errors, "type_mismatch"),
        high_risk_cases=_select_high_risk_errors(sorted_errors),
    )


def _metrics_to_payload(metrics: MetricsSummary) -> MetricsPayload:
    return {
        "total": metrics.total,
        "true_positive": metrics.true_positive,
        "false_positive": metrics.false_positive,
        "true_negative": metrics.true_negative,
        "false_negative": metrics.false_negative,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "f1": metrics.f1,
        "accuracy": metrics.accuracy,
    }


def _type_metrics_to_payload(type_metrics: TypeMetricsSummary) -> TypeMetricsPayload:
    return {
        "hallucination_type": type_metrics.hallucination_type,
        "label_count": type_metrics.label_count,
        "predicted_count": type_metrics.predicted_count,
        "true_positive_count": type_metrics.true_positive_count,
        "mismatch_count": type_metrics.mismatch_count,
    }


def _result_to_payload(result: DetectionResult) -> ResultPayload:
    return {
        "case_id": result.case_id,
        "is_hallucination": result.is_hallucination,
        "hallucination_type": result.hallucination_type,
        "reasons": list(result.reasons),
        "rule_ids": list(result.rule_ids),
    }


def _rule_hit_summary_to_payload(summary: RuleHitSummary) -> RuleHitPayload:
    metadata = summary.metadata
    return {
        "rule_id": metadata.rule_id,
        "hallucination_type": metadata.hallucination_type,
        "risk_level": metadata.risk_level,
        "description": metadata.description,
        "trigger_intent": metadata.trigger_intent,
        "hit_count": summary.hit_count,
        "case_ids": list(summary.case_ids),
    }


def _error_to_payload(error_case: ErrorCase) -> ErrorPayload:
    return {
        "case_id": error_case.case_id,
        "error_type": error_case.error_type,
        "expected": _label_to_payload(error_case.expected),
        "predicted": _result_to_payload(error_case.predicted),
    }


def _label_to_payload(label: GroundTruthLabel) -> LabelPayload:
    return {
        "case_id": label.case_id,
        "is_hallucination": label.is_hallucination,
        "hallucination_type": label.hallucination_type,
        "detail": label.detail,
    }


def _summarize_rule_hits(results: Iterable[DetectionResult]) -> tuple[RuleHitSummary, ...]:
    metadata_by_rule_id = {rule.metadata.rule_id: rule.metadata for rule in DETECTION_RULES}
    case_ids_by_rule_id: dict[str, set[str]] = {}

    for result in results:
        for rule_id in result.rule_ids:
            if rule_id not in metadata_by_rule_id:
                continue
            case_ids_by_rule_id.setdefault(rule_id, set()).add(result.case_id)

    summaries = tuple(
        RuleHitSummary(
            metadata=metadata_by_rule_id[rule_id],
            case_ids=tuple(sorted(case_ids)),
        )
        for rule_id, case_ids in case_ids_by_rule_id.items()
    )
    return tuple(sorted(summaries, key=_rule_hit_summary_sort_key))


def _rule_hit_summary_sort_key(summary: RuleHitSummary) -> tuple[int, int, str]:
    return (
        -summary.hit_count,
        _risk_sort_order(summary.metadata.risk_level),
        summary.metadata.rule_id,
    )


def _risk_sort_order(risk_level: RuleRiskLevel) -> int:
    return {"high": 0, "medium": 1, "low": 2}[risk_level]


def _select_high_risk_errors(error_cases: Iterable[ErrorCase]) -> tuple[ErrorCase, ...]:
    high_risk_by_id: dict[str, ErrorCase] = {}
    for error_case in error_cases:
        if _is_high_risk(error_case):
            high_risk_by_id[error_case.case_id] = error_case
    return tuple(high_risk_by_id[case_id] for case_id in sorted(high_risk_by_id))


def _is_high_risk(error_case: ErrorCase) -> bool:
    return (
        error_case.error_type == "false_negative"
        or error_case.expected.hallucination_type == "安全误导"
        or error_case.predicted.hallucination_type == "安全误导"
    )


def _render_result_row(result: DetectionResult) -> str:
    return (
        f"| {_format_cell(result.case_id)} "
        f"| {_format_cell(_format_bool(result.is_hallucination))} "
        f"| {_format_cell(result.hallucination_type)} "
        f"| {_format_cell(_join_values(result.rule_ids))} "
        f"| {_format_cell(_join_values(result.reasons))} |"
    )


def _render_rule_hit_summary(summaries: Iterable[RuleHitSummary]) -> list[str]:
    summaries_tuple = tuple(summaries)
    if not summaries_tuple:
        return ["- 无"]

    lines = [
        "| 规则 ID | 幻觉类型 | 风险等级 | 命中数 | 样本 ID | 触发意图 | 说明 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend(_render_rule_hit_summary_row(summary) for summary in summaries_tuple)
    return lines


def _render_type_metrics(type_metrics: Iterable[TypeMetricsSummary]) -> list[str]:
    type_metrics_tuple = tuple(type_metrics)
    if not type_metrics_tuple:
        return ["- 无"]

    lines = [
        "| 幻觉类型 | 标注数 | 预测数 | 命中数 | 错配数 |",
        "| --- | --- | --- | --- | --- |",
    ]
    lines.extend(_render_type_metrics_row(type_metric) for type_metric in type_metrics_tuple)
    return lines


def _render_type_metrics_row(type_metrics: TypeMetricsSummary) -> str:
    return (
        f"| {_format_cell(type_metrics.hallucination_type)} "
        f"| {type_metrics.label_count} "
        f"| {type_metrics.predicted_count} "
        f"| {type_metrics.true_positive_count} "
        f"| {type_metrics.mismatch_count} |"
    )


def _render_rule_hit_summary_row(summary: RuleHitSummary) -> str:
    metadata = summary.metadata
    return (
        f"| {_format_cell(metadata.rule_id)} "
        f"| {_format_cell(metadata.hallucination_type)} "
        f"| {_format_cell(metadata.risk_level)} "
        f"| {summary.hit_count} "
        f"| {_format_cell(_join_values(summary.case_ids))} "
        f"| {_format_cell(metadata.trigger_intent)} "
        f"| {_format_cell(metadata.description)} |"
    )


def _render_error_lines(
    error_cases: Iterable[ErrorCase],
    formatter: Callable[[ErrorCase], str],
) -> list[str]:
    lines = [formatter(error_case) for error_case in error_cases]
    if not lines:
        return ["- 无"]
    return lines


def _format_false_negative(error_case: ErrorCase) -> str:
    expected_type = _format_text(error_case.expected.hallucination_type)
    return (
        f"- {error_case.case_id}: 期望 {expected_type}，预测为非幻觉。"
        f"人工说明：{_format_text(error_case.expected.detail)}"
    )


def _format_false_positive(error_case: ErrorCase) -> str:
    predicted_type = _format_text(error_case.predicted.hallucination_type)
    return (
        f"- {error_case.case_id}: 预测 {predicted_type}；"
        f"原因：{_format_text(_join_values(error_case.predicted.reasons))}"
    )


def _format_type_mismatch(error_case: ErrorCase) -> str:
    expected_type = _format_text(error_case.expected.hallucination_type)
    predicted_type = _format_text(error_case.predicted.hallucination_type)
    return f"- {error_case.case_id}: 期望 {expected_type}，预测 {predicted_type}。"


def _format_high_risk_case(error_case: ErrorCase) -> str:
    expected_type = _format_text(error_case.expected.hallucination_type)
    predicted_type = _format_text(error_case.predicted.hallucination_type)
    return (
        f"- {error_case.case_id}: {error_case.error_type}，"
        f"期望 {expected_type}，预测 {predicted_type}。"
    )


def _format_rate(value: float) -> str:
    return f"{value:.3f}"


def _format_bool(value: bool) -> str:
    return "是" if value else "否"


def _join_values(values: Iterable[str]) -> str:
    values_tuple = tuple(values)
    if not values_tuple:
        return "-"
    return "；".join(values_tuple)


def _format_cell(value: object) -> str:
    return _format_text(value).replace("|", "\\|").replace("\n", " ")


def _format_text(value: object) -> str:
    if value is None:
        return "-"
    return str(value)


__all__ = [
    "LIMITATIONS",
    "build_report_payload",
    "render_json_report",
    "render_markdown_report",
]
