from dataclasses import FrozenInstanceError

import pytest

from customer_service_hallucination_audit.models import (
    DetectionResult,
    ErrorCase,
    GroundTruthLabel,
    MetricsSummary,
    ReplyCase,
)


def test_reply_case_captures_source_fields() -> None:
    reply = ReplyCase(
        case_id="h01",
        user_question="你们支持30天无理由退货吗？",
        system_reply="支持的，我们全品类支持30天无理由退货。",
        knowledge_base="普通商品支持7天无理由退货。",
    )

    assert reply.case_id == "h01"
    assert reply.user_question == "你们支持30天无理由退货吗？"
    assert reply.system_reply == "支持的，我们全品类支持30天无理由退货。"
    assert reply.knowledge_base == "普通商品支持7天无理由退货。"


def test_ground_truth_label_supports_non_hallucination() -> None:
    label = GroundTruthLabel(
        case_id="h12",
        is_hallucination=False,
        hallucination_type=None,
        detail="回复与知识库一致。",
    )

    assert label.is_hallucination is False
    assert label.hallucination_type is None


def test_detection_result_records_reasons_and_triggered_rules() -> None:
    result = DetectionResult(
        case_id="h03",
        is_hallucination=True,
        hallucination_type="能力越界",
        reasons=("系统未接入物流查询接口，却声称查到了具体位置。",),
        rule_ids=("capability.unavailable_lookup",),
    )

    assert result.hallucination_type == "能力越界"
    assert result.reasons == ("系统未接入物流查询接口，却声称查到了具体位置。",)
    assert result.rule_ids == ("capability.unavailable_lookup",)


def test_models_are_immutable() -> None:
    reply = ReplyCase(
        case_id="h16",
        user_question="商品图片上的颜色准吗？",
        system_reply="不同屏幕可能会有轻微色差。",
        knowledge_base="商品图片可能与实物存在轻微色差。",
    )

    with pytest.raises(FrozenInstanceError):
        reply.case_id = "changed"


def test_metrics_summary_exposes_confusion_matrix_and_rates() -> None:
    metrics = MetricsSummary(
        true_positive=18,
        false_positive=0,
        true_negative=2,
        false_negative=0,
        precision=1.0,
        recall=1.0,
        f1=1.0,
    )

    assert metrics.total == 20
    assert metrics.accuracy == 1.0


def test_error_case_keeps_expected_and_predicted_context() -> None:
    error = ErrorCase(
        case_id="h20",
        error_type="false_negative",
        expected=GroundTruthLabel(
            case_id="h20",
            is_hallucination=True,
            hallucination_type="信息遗漏",
            detail="遗漏尺码偏大信息。",
        ),
        predicted=DetectionResult(
            case_id="h20",
            is_hallucination=False,
            hallucination_type=None,
            reasons=("未触发规则。",),
            rule_ids=(),
        ),
    )

    assert error.case_id == "h20"
    assert error.expected.hallucination_type == "信息遗漏"
    assert error.predicted.hallucination_type is None
