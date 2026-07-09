from __future__ import annotations

import json

import pytest

from customer_service_hallucination_audit.models import (
    DetectionResult,
    ErrorCase,
    GroundTruthLabel,
    HallucinationType,
    MetricsSummary,
)
from customer_service_hallucination_audit.reporting import (
    build_report_payload,
    render_json_report,
    render_markdown_report,
)


def label(
    case_id: str,
    *,
    is_hallucination: bool,
    hallucination_type: HallucinationType | None = None,
    detail: str = "人工标注说明",
) -> GroundTruthLabel:
    return GroundTruthLabel(
        case_id=case_id,
        is_hallucination=is_hallucination,
        hallucination_type=hallucination_type,
        detail=detail,
    )


def result(
    case_id: str,
    *,
    is_hallucination: bool,
    hallucination_type: HallucinationType | None = None,
    reasons: tuple[str, ...] = ("检测原因",),
    rule_ids: tuple[str, ...] = ("test.rule",),
) -> DetectionResult:
    return DetectionResult(
        case_id=case_id,
        is_hallucination=is_hallucination,
        hallucination_type=hallucination_type,
        reasons=reasons,
        rule_ids=rule_ids if is_hallucination else (),
    )


def summary() -> MetricsSummary:
    return MetricsSummary(
        true_positive=1,
        false_positive=1,
        true_negative=0,
        false_negative=1,
        precision=0.5,
        recall=0.5,
        f1=0.5,
    )


def sample_results() -> tuple[DetectionResult, ...]:
    return (
        result(
            "h03",
            is_hallucination=False,
            hallucination_type=None,
            reasons=("未触发确定性幻觉规则。",),
            rule_ids=(),
        ),
        result("h01", is_hallucination=True, hallucination_type="政策编造"),
        result("h02", is_hallucination=True, hallucination_type="优惠编造"),
    )


def sample_errors() -> tuple[ErrorCase, ...]:
    false_negative = ErrorCase(
        case_id="h03",
        error_type="false_negative",
        expected=label(
            "h03",
            is_hallucination=True,
            hallucination_type="安全误导",
            detail="应提示咨询医生。",
        ),
        predicted=result(
            "h03",
            is_hallucination=False,
            reasons=("未触发确定性幻觉规则。",),
            rule_ids=(),
        ),
    )
    false_positive = ErrorCase(
        case_id="h02",
        error_type="false_positive",
        expected=label("h02", is_hallucination=False, detail="人工认为回复一致。"),
        predicted=result("h02", is_hallucination=True, hallucination_type="优惠编造"),
    )
    type_mismatch = ErrorCase(
        case_id="h01",
        error_type="type_mismatch",
        expected=label("h01", is_hallucination=True, hallucination_type="政策编造"),
        predicted=result("h01", is_hallucination=True, hallucination_type="信息编造"),
    )
    return (false_negative, false_positive, type_mismatch)


def test_build_report_payload_contains_stable_json_sections() -> None:
    payload = build_report_payload(sample_results(), summary(), sample_errors())

    assert tuple(payload) == (
        "metrics",
        "results",
        "false_positives",
        "false_negatives",
        "type_mismatches",
        "high_risk_cases",
        "limitations",
    )
    assert payload["metrics"] == {
        "total": 3,
        "true_positive": 1,
        "false_positive": 1,
        "true_negative": 0,
        "false_negative": 1,
        "precision": 0.5,
        "recall": 0.5,
        "f1": 0.5,
        "accuracy": pytest.approx(1 / 3),
    }
    assert [item["case_id"] for item in payload["results"]] == ["h01", "h02", "h03"]
    assert [item["case_id"] for item in payload["false_positives"]] == ["h02"]
    assert [item["case_id"] for item in payload["false_negatives"]] == ["h03"]
    assert [item["case_id"] for item in payload["type_mismatches"]] == ["h01"]
    assert [item["case_id"] for item in payload["high_risk_cases"]] == ["h03"]
    assert payload["limitations"]


def test_render_json_report_outputs_deterministic_utf8_json() -> None:
    report = render_json_report(sample_results(), summary(), sample_errors())

    assert report.endswith("\n")
    decoded = json.loads(report)
    assert decoded["results"][0]["case_id"] == "h01"
    assert decoded["false_negatives"][0]["expected"]["hallucination_type"] == "安全误导"
    assert "安全误导" in report


def test_render_markdown_report_contains_required_sections_and_tables() -> None:
    report = render_markdown_report(sample_results(), summary(), sample_errors())

    assert report.startswith("# 客服回复幻觉检测报告\n")
    assert "## 总体指标" in report
    assert "| Precision | 0.500 |" in report
    assert "## 分类结果" in report
    assert "| h01 | 是 | 政策编造 | test.rule | 检测原因 |" in report
    assert "## 漏检" in report
    assert "- h03: 期望 安全误导，预测为非幻觉。人工说明：应提示咨询医生。" in report
    assert "## 误报" in report
    assert "- h02: 预测 优惠编造；原因：检测原因" in report
    assert "## 类型错误" in report
    assert "- h01: 期望 政策编造，预测 信息编造。" in report
    assert "## 高风险案例" in report
    assert "## 局限性" in report


def test_render_markdown_report_uses_empty_list_placeholder() -> None:
    report = render_markdown_report(
        (result("h01", is_hallucination=False, reasons=("未触发确定性幻觉规则。",), rule_ids=()),),
        MetricsSummary(
            true_positive=0,
            false_positive=0,
            true_negative=1,
            false_negative=0,
            precision=0.0,
            recall=0.0,
            f1=0.0,
        ),
        (),
    )

    assert "## 漏检\n\n- 无" in report
    assert "## 误报\n\n- 无" in report
    assert "## 类型错误\n\n- 无" in report
    assert "## 高风险案例\n\n- 无" in report
