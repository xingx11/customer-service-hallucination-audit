from dataclasses import FrozenInstanceError

import pytest

from customer_service_hallucination_audit.models import (
    DetectionResult,
    ErrorCase,
    GroundTruthLabel,
    MetricsSummary,
    ReplyCase,
    RuleMetadata,
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


@pytest.mark.parametrize(
    ("is_hallucination", "hallucination_type", "expected_message"),
    [
        (False, "政策编造", "must be None when is_hallucination is false"),
        (True, None, "must be set when is_hallucination is true"),
    ],
)
def test_ground_truth_label_rejects_invalid_hallucination_type_state(
    is_hallucination: bool,
    hallucination_type: str | None,
    expected_message: str,
) -> None:
    with pytest.raises(ValueError, match=expected_message):
        GroundTruthLabel(
            case_id="h01",
            is_hallucination=is_hallucination,
            hallucination_type=hallucination_type,
            detail="人工标注说明。",
        )


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


def test_rule_metadata_describes_detector_rule() -> None:
    metadata = RuleMetadata(
        rule_id="policy.return_window_fabrication",
        hallucination_type="政策编造",
        risk_level="high",
        description="回复把7天无理由退货扩展为30天无理由退货。",
        trigger_intent="识别退货时效和运费承担政策编造。",
    )

    assert metadata.rule_id == "policy.return_window_fabrication"
    assert metadata.hallucination_type == "政策编造"
    assert metadata.risk_level == "high"
    assert metadata.description
    assert metadata.trigger_intent


@pytest.mark.parametrize(
    ("is_hallucination", "hallucination_type", "expected_message"),
    [
        (False, "政策编造", "must be None when is_hallucination is false"),
        (True, None, "must be set when is_hallucination is true"),
    ],
)
def test_detection_result_rejects_invalid_hallucination_type_state(
    is_hallucination: bool,
    hallucination_type: str | None,
    expected_message: str,
) -> None:
    with pytest.raises(ValueError, match=expected_message):
        DetectionResult(
            case_id="h01",
            is_hallucination=is_hallucination,
            hallucination_type=hallucination_type,
            reasons=("检测原因",),
            rule_ids=("test.rule",) if is_hallucination else (),
        )


@pytest.mark.parametrize(
    ("field_name", "expected_message"),
    [
        ("rule_id", "rule_id must not be empty"),
        ("description", "description must not be empty"),
        ("trigger_intent", "trigger_intent must not be empty"),
    ],
)
def test_rule_metadata_rejects_empty_required_text(
    field_name: str,
    expected_message: str,
) -> None:
    values = {
        "rule_id": "test.rule",
        "hallucination_type": "政策编造",
        "risk_level": "medium",
        "description": "规则说明。",
        "trigger_intent": "触发意图。",
    }
    values[field_name] = ""

    with pytest.raises(ValueError, match=expected_message):
        RuleMetadata(**values)


def test_rule_metadata_rejects_unknown_risk_level() -> None:
    with pytest.raises(ValueError, match="Unknown risk_level 'urgent'"):
        RuleMetadata(
            rule_id="test.rule",
            hallucination_type="政策编造",
            risk_level="urgent",
            description="规则说明。",
            trigger_intent="触发意图。",
        )


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
    )

    assert metrics.total == 20
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.f1 == 1.0
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


def test_error_case_rejects_mismatched_case_ids() -> None:
    expected = GroundTruthLabel(
        case_id="h20",
        is_hallucination=True,
        hallucination_type="信息遗漏",
        detail="遗漏尺码偏大信息。",
    )
    predicted = DetectionResult(
        case_id="h21",
        is_hallucination=False,
        hallucination_type=None,
        reasons=("未触发规则。",),
        rule_ids=(),
    )

    with pytest.raises(ValueError, match="case_id must match expected and predicted case IDs"):
        ErrorCase(
            case_id="h20",
            error_type="false_negative",
            expected=expected,
            predicted=predicted,
        )
