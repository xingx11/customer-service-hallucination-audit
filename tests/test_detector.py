import json
from pathlib import Path

import pytest

from customer_service_hallucination_audit.detector import (
    DETECTION_RULES,
    LLM_API_KEY_ENV_VAR,
    LLM_ENDPOINT_ENV_VAR,
    LLM_MODEL_ENV_VAR,
    LlmConfigurationError,
    LlmOutputValidationError,
    UnknownDetectorError,
    build_llm_prompt,
    create_llm_detector,
    detect_replies,
    detect_reply,
    deterministic_detector,
    llm_detector,
    mock_detector,
    parse_llm_detection_result,
    select_detector,
)
from customer_service_hallucination_audit.io import load_audit_dataset, load_reply_cases
from customer_service_hallucination_audit.models import (
    HALLUCINATION_TYPES,
    RULE_RISK_LEVELS,
    AuditDataset,
    HallucinationType,
    ReplyCase,
)

REPLIES_PATH = Path(__file__).resolve().parents[1] / "data" / "replies.json"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
STAGE_2_ROBUSTNESS_REPLIES_PATH = FIXTURES_DIR / "stage_2_robustness_replies.json"
STAGE_2_ROBUSTNESS_GROUND_TRUTH_PATH = FIXTURES_DIR / "stage_2_robustness_ground_truth.json"


class FakeLlmClient:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.outputs.pop(0)


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


def test_deterministic_adapter_matches_rule_detector() -> None:
    replies = tuple(load_default_reply_cases()[case_id] for case_id in ("h01", "h12", "h20"))

    assert deterministic_detector(replies) == detect_replies(replies)
    assert select_detector("deterministic")(replies) == detect_replies(replies)


def test_mock_adapter_returns_stable_synthetic_results() -> None:
    replies = tuple(load_default_reply_cases()[case_id] for case_id in ("h01", "h02", "h03"))

    results = mock_detector(replies)

    assert tuple(result.case_id for result in results) == ("h01", "h02", "h03")
    assert results[0].is_hallucination is True
    assert results[0].hallucination_type == "信息编造"
    assert results[0].rule_ids == ("mock.synthetic_signal",)
    assert results[1].is_hallucination is False
    assert results[1].hallucination_type is None
    assert results[1].rule_ids == ()
    assert select_detector("mock")(replies) == results


def test_create_llm_detector_uses_fake_client_and_parser_offline() -> None:
    replies = tuple(load_default_reply_cases()[case_id] for case_id in ("h01", "h12"))
    client = FakeLlmClient(
        [
            json.dumps(
                {
                    "case_id": "h01",
                    "is_hallucination": True,
                    "hallucination_type": HALLUCINATION_TYPES[0],
                    "reasons": ["LLM flagged a policy mismatch."],
                    "rule_ids": ["llm.policy_return_window"],
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "case_id": "h12",
                    "is_hallucination": False,
                    "hallucination_type": None,
                    "reasons": ["LLM found the reply consistent."],
                    "rule_ids": [],
                },
                ensure_ascii=False,
            ),
        ]
    )

    detector = create_llm_detector(client)
    results = detector(replies)

    assert tuple(result.case_id for result in results) == ("h01", "h12")
    assert results[0].is_hallucination is True
    assert results[0].hallucination_type == HALLUCINATION_TYPES[0]
    assert results[0].rule_ids == ("llm.policy_return_window",)
    assert results[1].is_hallucination is False
    assert results[1].hallucination_type is None
    assert len(client.prompts) == 2
    assert "case_id: h01" in client.prompts[0]
    assert replies[0].system_reply in client.prompts[0]


def test_llm_detector_requires_environment_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for env_var in (LLM_API_KEY_ENV_VAR, LLM_ENDPOINT_ENV_VAR, LLM_MODEL_ENV_VAR):
        monkeypatch.delenv(env_var, raising=False)
    replies = tuple(load_default_reply_cases()[case_id] for case_id in ("h01",))

    with pytest.raises(LlmConfigurationError) as exc_info:
        llm_detector(replies)

    message = str(exc_info.value)
    assert "LLM detector requires environment variables" in message
    assert LLM_API_KEY_ENV_VAR in message
    assert LLM_ENDPOINT_ENV_VAR in message
    assert LLM_MODEL_ENV_VAR in message
    with pytest.raises(LlmConfigurationError):
        select_detector("llm")(replies)


def test_select_detector_rejects_unknown_adapter() -> None:
    with pytest.raises(
        UnknownDetectorError,
        match="Unknown detector adapter 'unknown'. Expected one of: deterministic, mock, llm",
    ):
        select_detector("unknown")


def test_build_llm_prompt_uses_only_reply_evidence_and_schema() -> None:
    reply = load_default_reply_cases()["h01"]

    prompt = build_llm_prompt(reply)

    assert reply.case_id in prompt
    assert reply.user_question in prompt
    assert reply.system_reply in prompt
    assert reply.knowledge_base in prompt
    assert "只依据用户问题、系统回复和知识库" in prompt
    assert "不要使用人工真值" in prompt
    assert '"case_id"' in prompt
    assert '"is_hallucination"' in prompt
    assert '"hallucination_type"' in prompt
    assert all(hallucination_type in prompt for hallucination_type in HALLUCINATION_TYPES)


def test_parse_llm_detection_result_accepts_valid_hallucination_output() -> None:
    reply = load_default_reply_cases()["h01"]
    raw_output = json.dumps(
        {
            "case_id": "h01",
            "is_hallucination": True,
            "hallucination_type": "政策编造",
            "reasons": ["回复把7天无理由退货扩展为30天。"],
            "rule_ids": ["llm.policy_fabrication"],
        },
        ensure_ascii=False,
    )

    result = parse_llm_detection_result(reply, raw_output)

    assert result.case_id == "h01"
    assert result.is_hallucination is True
    assert result.hallucination_type == "政策编造"
    assert result.reasons == ("回复把7天无理由退货扩展为30天。",)
    assert result.rule_ids == ("llm.policy_fabrication",)


def test_parse_llm_detection_result_accepts_valid_non_hallucination_output() -> None:
    reply = load_default_reply_cases()["h12"]
    raw_output = json.dumps(
        {
            "case_id": "h12",
            "is_hallucination": False,
            "hallucination_type": None,
            "reasons": ["回复与知识库一致。"],
            "rule_ids": [],
        },
        ensure_ascii=False,
    )

    result = parse_llm_detection_result(reply, raw_output)

    assert result.case_id == "h12"
    assert result.is_hallucination is False
    assert result.hallucination_type is None
    assert result.reasons == ("回复与知识库一致。",)
    assert result.rule_ids == ()


@pytest.mark.parametrize(
    ("raw_output", "expected_message"),
    [
        ("不是 JSON", "LLM output must be valid JSON"),
        (
            json.dumps(
                {
                    "case_id": "h01",
                    "is_hallucination": True,
                    "hallucination_type": "政策编造",
                    "rule_ids": [],
                },
                ensure_ascii=False,
            ),
            "LLM output missing required field 'reasons'",
        ),
        (
            json.dumps(
                {
                    "case_id": "h02",
                    "is_hallucination": True,
                    "hallucination_type": "政策编造",
                    "reasons": ["ID 不匹配。"],
                    "rule_ids": [],
                },
                ensure_ascii=False,
            ),
            "LLM output case_id 'h02' does not match reply case_id 'h01'",
        ),
        (
            json.dumps(
                {
                    "case_id": "h01",
                    "is_hallucination": True,
                    "hallucination_type": "未知类型",
                    "reasons": ["未知类型。"],
                    "rule_ids": [],
                },
                ensure_ascii=False,
            ),
            "Unknown hallucination_type '未知类型'",
        ),
    ],
)
def test_parse_llm_detection_result_rejects_invalid_output(
    raw_output: str,
    expected_message: str,
) -> None:
    reply = load_default_reply_cases()["h01"]

    with pytest.raises(LlmOutputValidationError, match=expected_message):
        parse_llm_detection_result(reply, raw_output)


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


def test_detection_rules_have_complete_structured_metadata() -> None:
    rule_ids = [rule.metadata.rule_id for rule in DETECTION_RULES]

    assert len(rule_ids) == len(set(rule_ids))
    assert all(rule.metadata.rule_id for rule in DETECTION_RULES)
    assert all(rule.metadata.hallucination_type in HALLUCINATION_TYPES for rule in DETECTION_RULES)
    assert all(rule.metadata.risk_level in RULE_RISK_LEVELS for rule in DETECTION_RULES)
    assert all(rule.metadata.description for rule in DETECTION_RULES)
    assert all(rule.metadata.trigger_intent for rule in DETECTION_RULES)


def test_detect_reply_outputs_metadata_for_triggered_rule() -> None:
    replies = load_default_reply_cases()
    rules_by_id = {rule.metadata.rule_id: rule for rule in DETECTION_RULES}

    result = detect_reply(replies["h01"])
    triggered_rule = rules_by_id[result.rule_ids[0]]

    assert result.rule_ids == (triggered_rule.metadata.rule_id,)
    assert result.hallucination_type == triggered_rule.metadata.hallucination_type
    assert result.reasons == (triggered_rule.metadata.description,)


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
