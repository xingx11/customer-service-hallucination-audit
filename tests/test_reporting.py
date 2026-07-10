from __future__ import annotations

import json

import pytest

from customer_service_hallucination_audit.models import (
    DetectionResult,
    ErrorCase,
    GroundTruthLabel,
    HallucinationType,
    MetricsSummary,
    TypeMetricsSummary,
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
    )


def sample_type_metrics() -> tuple[TypeMetricsSummary, ...]:
    return (
        TypeMetricsSummary(
            hallucination_type="政策编造",
            label_count=1,
            predicted_count=1,
            true_positive_count=0,
            mismatch_count=1,
        ),
        TypeMetricsSummary(
            hallucination_type="优惠编造",
            label_count=0,
            predicted_count=1,
            true_positive_count=0,
            mismatch_count=1,
        ),
        TypeMetricsSummary(
            hallucination_type="安全误导",
            label_count=1,
            predicted_count=0,
            true_positive_count=0,
            mismatch_count=1,
        ),
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
        result(
            "h01",
            is_hallucination=True,
            hallucination_type="政策编造",
            reasons=("退货规则命中",),
            rule_ids=("policy.return_window_fabrication",),
        ),
        result(
            "h02",
            is_hallucination=True,
            hallucination_type="优惠编造",
            reasons=("优惠规则命中",),
            rule_ids=("discount.coupon_fabrication",),
        ),
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
    payload = build_report_payload(
        sample_results(),
        summary(),
        sample_type_metrics(),
        sample_errors(),
    )

    assert tuple(payload) == (
        "metrics",
        "type_metrics",
        "results",
        "rule_hit_summary",
        "false_positives",
        "false_negatives",
        "type_mismatches",
        "high_risk_rationale",
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
    assert payload["type_metrics"] == [
        {
            "hallucination_type": "政策编造",
            "label_count": 1,
            "predicted_count": 1,
            "true_positive_count": 0,
            "mismatch_count": 1,
        },
        {
            "hallucination_type": "优惠编造",
            "label_count": 0,
            "predicted_count": 1,
            "true_positive_count": 0,
            "mismatch_count": 1,
        },
        {
            "hallucination_type": "安全误导",
            "label_count": 1,
            "predicted_count": 0,
            "true_positive_count": 0,
            "mismatch_count": 1,
        },
    ]
    assert [item["case_id"] for item in payload["results"]] == ["h01", "h02", "h03"]
    assert [item["case_id"] for item in payload["false_positives"]] == ["h02"]
    assert [item["case_id"] for item in payload["false_negatives"]] == ["h03"]
    assert [item["case_id"] for item in payload["type_mismatches"]] == ["h01"]
    assert payload["high_risk_rationale"] == [
        "纳入所有漏检案例。",
        "纳入人工标注或预测类型为安全误导的错误案例。",
        "输出按样本 ID 稳定排序，便于复现和 diff 审阅。",
    ]
    assert [item["case_id"] for item in payload["high_risk_cases"]] == ["h03"]
    assert payload["rule_hit_summary"] == [
        {
            "rule_id": "policy.return_window_fabrication",
            "hallucination_type": "政策编造",
            "risk_level": "high",
            "description": (
                "回复把7天无理由退货扩展为30天无理由退货，并承诺商家承担非质量问题运费。"
            ),
            "trigger_intent": "识别退货时效和运费承担政策编造。",
            "hit_count": 1,
            "case_ids": ["h01"],
        },
        {
            "rule_id": "discount.coupon_fabrication",
            "hallucination_type": "优惠编造",
            "risk_level": "medium",
            "description": "回复承诺了知识库明确不存在的优惠券或优惠活动。",
            "trigger_intent": "识别不存在的优惠券或优惠活动承诺。",
            "hit_count": 1,
            "case_ids": ["h02"],
        },
    ]
    assert payload["limitations"]


def test_build_report_payload_sorts_rule_hit_summary_by_frequency_then_risk() -> None:
    results = (
        result(
            "h01",
            is_hallucination=True,
            hallucination_type="政策编造",
            rule_ids=("policy.return_window_fabrication",),
        ),
        result(
            "h02",
            is_hallucination=True,
            hallucination_type="优惠编造",
            rule_ids=("discount.coupon_fabrication",),
        ),
        result(
            "h03",
            is_hallucination=True,
            hallucination_type="优惠编造",
            rule_ids=("discount.coupon_fabrication",),
        ),
    )

    payload = build_report_payload(results, summary(), sample_type_metrics(), ())

    assert [item["rule_id"] for item in payload["rule_hit_summary"]] == [
        "discount.coupon_fabrication",
        "policy.return_window_fabrication",
    ]
    assert payload["rule_hit_summary"][0]["hit_count"] == 2
    assert payload["rule_hit_summary"][0]["case_ids"] == ["h02", "h03"]


def test_render_json_report_outputs_deterministic_utf8_json() -> None:
    report = render_json_report(
        sample_results(),
        summary(),
        sample_type_metrics(),
        sample_errors(),
    )

    assert report.endswith("\n")
    decoded = json.loads(report)
    assert decoded["type_metrics"][0]["hallucination_type"] == "政策编造"
    assert decoded["results"][0]["case_id"] == "h01"
    assert decoded["rule_hit_summary"][0]["risk_level"] == "high"
    assert decoded["false_negatives"][0]["expected"]["hallucination_type"] == "安全误导"
    assert "安全误导" in report


def test_render_markdown_report_contains_required_sections_and_tables() -> None:
    report = render_markdown_report(
        sample_results(),
        summary(),
        sample_type_metrics(),
        sample_errors(),
    )

    assert report.startswith("# 客服回复幻觉检测报告\n")
    assert "## 总体指标" in report
    assert "| Precision | 0.500 |" in report
    assert "## 类型表现" in report
    assert "| 幻觉类型 | 标注数 | 预测数 | 命中数 | 错配数 |" in report
    assert "| 政策编造 | 1 | 1 | 0 | 1 |" in report
    assert "## 分类结果" in report
    assert "| h01 | 是 | 政策编造 | policy.return_window_fabrication | 退货规则命中 |" in report
    assert "## 规则命中摘要" in report
    assert (
        "| policy.return_window_fabrication | 政策编造 | high | 1 | h01 | "
        "识别退货时效和运费承担政策编造。 | "
        "回复把7天无理由退货扩展为30天无理由退货，并承诺商家承担非质量问题运费。 |" in report
    )
    assert "## 漏检" in report
    assert "- h03: 期望 安全误导，预测为非幻觉。人工说明：应提示咨询医生。" in report
    assert "## 误报" in report
    assert "- h02: 预测 优惠编造；原因：检测原因" in report
    assert "## 类型错误" in report
    assert "- h01: 期望 政策编造，预测 信息编造。" in report
    assert "## 高风险案例" in report
    assert "- 纳入所有漏检案例。" in report
    assert "- 输出按样本 ID 稳定排序，便于复现和 diff 审阅。" in report
    assert "## 局限性" in report


def test_render_markdown_report_uses_empty_list_placeholder() -> None:
    report = render_markdown_report(
        (result("h01", is_hallucination=False, reasons=("未触发确定性幻觉规则。",), rule_ids=()),),
        MetricsSummary(
            true_positive=0,
            false_positive=0,
            true_negative=1,
            false_negative=0,
        ),
        (),
        (),
    )

    assert "## 漏检\n\n- 无" in report
    assert "## 误报\n\n- 无" in report
    assert "## 类型错误\n\n- 无" in report
    assert "## 高风险案例\n\n筛选与排序依据：" in report
    assert "- 输出按样本 ID 稳定排序，便于复现和 diff 审阅。\n\n- 无" in report
