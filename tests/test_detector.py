from pathlib import Path

import pytest

from customer_service_hallucination_audit.detector import detect_replies, detect_reply
from customer_service_hallucination_audit.io import load_reply_cases
from customer_service_hallucination_audit.models import HallucinationType, ReplyCase

REPLIES_PATH = Path(__file__).resolve().parents[1] / "data" / "replies.json"


def load_default_reply_cases() -> dict[str, ReplyCase]:
    return {reply.case_id: reply for reply in load_reply_cases(REPLIES_PATH)}


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
