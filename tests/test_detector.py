from pathlib import Path

import pytest

from customer_service_hallucination_audit.detector import detect_replies, detect_reply
from customer_service_hallucination_audit.io import load_audit_dataset, load_reply_cases
from customer_service_hallucination_audit.models import (
    HALLUCINATION_TYPES,
    AuditDataset,
    HallucinationType,
    ReplyCase,
)

REPLIES_PATH = Path(__file__).resolve().parents[1] / "data" / "replies.json"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
STAGE_2_ROBUSTNESS_REPLIES_PATH = FIXTURES_DIR / "stage_2_robustness_replies.json"
STAGE_2_ROBUSTNESS_GROUND_TRUTH_PATH = FIXTURES_DIR / "stage_2_robustness_ground_truth.json"


def load_default_reply_cases() -> dict[str, ReplyCase]:
    return {reply.case_id: reply for reply in load_reply_cases(REPLIES_PATH)}


def load_stage_2_robustness_dataset() -> AuditDataset:
    return load_audit_dataset(
        replies_path=STAGE_2_ROBUSTNESS_REPLIES_PATH,
        labels_path=STAGE_2_ROBUSTNESS_GROUND_TRUTH_PATH,
    )


@pytest.mark.parametrize(
    ("case_id", "expected_type", "expected_rule_id"),
    [
        ("h01", "政策编造", "policy.return_window_fabrication"),
        ("h04", "政策偏差", "policy.invoice_deviation"),
        ("h02", "参数编造", "parameter.bluetooth_fabrication"),
        ("h05", "优惠编造", "discount.coupon_fabrication"),
        ("h07", "信息编造", "information.return_address_fabrication"),
        ("h03", "能力越界", "capability.logistics_lookup"),
        ("h13", "安全误导", "safety.pregnancy_guidance"),
        ("h20", "信息遗漏", "omission.size_feedback"),
    ],
)
def test_detect_reply_classifies_planned_hallucination_types(
    case_id: str,
    expected_type: HallucinationType,
    expected_rule_id: str,
) -> None:
    replies = load_default_reply_cases()

    result = detect_reply(replies[case_id])

    assert result.case_id == case_id
    assert result.is_hallucination is True
    assert result.hallucination_type == expected_type
    assert result.reasons
    assert expected_rule_id in result.rule_ids


@pytest.mark.parametrize("case_id", ["h12", "h16"])
def test_detect_reply_leaves_consistent_replies_as_non_hallucination(case_id: str) -> None:
    replies = load_default_reply_cases()

    result = detect_reply(replies[case_id])

    assert result.case_id == case_id
    assert result.is_hallucination is False
    assert result.hallucination_type is None
    assert result.reasons == ("未触发确定性幻觉规则。",)
    assert result.rule_ids == ()


def test_detect_replies_preserves_input_order() -> None:
    replies = tuple(load_default_reply_cases()[case_id] for case_id in ("h12", "h03", "h20"))

    results = detect_replies(replies)

    assert tuple(result.case_id for result in results) == ("h12", "h03", "h20")
    assert tuple(result.hallucination_type for result in results) == (
        None,
        "能力越界",
        "信息遗漏",
    )


def test_detect_replies_flags_all_default_risky_cases_except_known_consistent_replies() -> None:
    replies = load_reply_cases(REPLIES_PATH)

    results = detect_replies(replies)

    non_hallucination_ids = {result.case_id for result in results if not result.is_hallucination}
    assert non_hallucination_ids == {"h12", "h16"}
    assert sum(result.is_hallucination for result in results) == 18


def test_detect_reply_uses_content_rules_not_case_ids() -> None:
    reply = ReplyCase(
        case_id="custom-logistics",
        user_question="我的快递到哪了？",
        system_reply="我帮您查了一下，您的包裹目前在南京转运中心，预计明天下午送达。",
        knowledge_base="无（客服系统未接入物流查询接口）",
    )

    result = detect_reply(reply)

    assert result.case_id == "custom-logistics"
    assert result.is_hallucination is True
    assert result.hallucination_type == "能力越界"
    assert result.rule_ids == ("capability.logistics_lookup",)


def test_stage_2_robustness_fixture_covers_planned_blind_spots() -> None:
    dataset = load_stage_2_robustness_dataset()

    positive_types = {
        label.hallucination_type
        for label in dataset.labels
        if label.is_hallucination and label.hallucination_type is not None
    }
    negative_count = sum(not label.is_hallucination for label in dataset.labels)
    details = "\n".join(label.detail for label in dataset.labels)

    assert len(dataset.replies) == len(dataset.labels)
    assert set(reply.case_id for reply in dataset.replies) == {
        label.case_id for label in dataset.labels
    }
    assert len(positive_types) >= 6
    assert positive_types <= set(HALLUCINATION_TYPES)
    assert negative_count >= 3
    assert all(label.detail.startswith(("盲区：", "困难负例：")) for label in dataset.labels)
    assert "同义改写" in details
    assert "信息遗漏" in details
    assert "安全敏感" in details


@pytest.mark.parametrize(
    ("case_id", "expected_rule_id"),
    [
        ("s2-policy-return-synonym", "policy.return_window_fabrication"),
        ("s2-policy-invoice-entry", "policy.invoice_deviation"),
        ("s2-parameter-bluetooth-synonym", "parameter.bluetooth_fabrication"),
        ("s2-discount-student-synonym", "discount.student_discount_fabrication"),
        ("s2-information-return-address-synonym", "information.return_address_fabrication"),
        ("s2-capability-logistics-synonym", "capability.logistics_lookup"),
        ("s2-safety-pregnancy-paraphrase", "safety.pregnancy_guidance"),
        ("s2-omission-size-feedback-paraphrase", "omission.size_feedback"),
    ],
)
def test_detect_reply_handles_stage_2_positive_boundary_cases(
    case_id: str,
    expected_rule_id: str,
) -> None:
    dataset = load_stage_2_robustness_dataset()
    replies_by_id = {reply.case_id: reply for reply in dataset.replies}
    labels_by_id = {label.case_id: label for label in dataset.labels}

    result = detect_reply(replies_by_id[case_id])
    expected = labels_by_id[case_id]

    assert expected.is_hallucination is True
    assert result.is_hallucination is True
    assert result.hallucination_type == expected.hallucination_type
    assert result.rule_ids == (expected_rule_id,)


@pytest.mark.parametrize(
    "case_id",
    [
        "s2-negative-coupon-denial",
        "s2-negative-invoice-policy",
        "s2-negative-logistics-boundary",
        "s2-negative-safety-caution",
    ],
)
def test_detect_reply_keeps_stage_2_hard_negatives_clean(case_id: str) -> None:
    dataset = load_stage_2_robustness_dataset()
    replies_by_id = {reply.case_id: reply for reply in dataset.replies}

    result = detect_reply(replies_by_id[case_id])

    assert result.is_hallucination is False
    assert result.hallucination_type is None
    assert result.rule_ids == ()
