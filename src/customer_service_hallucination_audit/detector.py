"""Deterministic offline rules for customer-service hallucination detection."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from customer_service_hallucination_audit.models import (
    DetectionResult,
    ReplyCase,
    RuleMetadata,
)

NO_RULE_REASON = "未触发确定性幻觉规则。"


@dataclass(frozen=True)
class DetectionRule:
    metadata: RuleMetadata
    reply_all: tuple[str, ...] = ()
    reply_any: tuple[str, ...] = ()
    reply_any_groups: tuple[tuple[str, ...], ...] = ()
    reply_none: tuple[str, ...] = ()
    knowledge_all: tuple[str, ...] = ()
    knowledge_any: tuple[str, ...] = ()

    def matches(self, reply_case: ReplyCase) -> bool:
        return (
            _contains_all(reply_case.system_reply, self.reply_all)
            and _contains_any(reply_case.system_reply, self.reply_any)
            and _contains_any_groups(reply_case.system_reply, self.reply_any_groups)
            and _contains_none(reply_case.system_reply, self.reply_none)
            and _contains_all(reply_case.knowledge_base, self.knowledge_all)
            and _contains_any(reply_case.knowledge_base, self.knowledge_any)
        )


DETECTION_RULES: tuple[DetectionRule, ...] = (
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="policy.return_window_fabrication",
            hallucination_type="政策编造",
            risk_level="high",
            description="回复把7天无理由退货扩展为30天无理由退货，并承诺商家承担非质量问题运费。",
            trigger_intent="识别退货时效和运费承担政策编造。",
        ),
        reply_any_groups=(
            (
                "30天无理由退货",
                "一个月内都能无理由退",
                "一个月内无理由退",
            ),
            (
                "来回运费我们包了",
                "运费也由我们承担",
                "运费由我们承担",
            ),
        ),
        reply_none=(
            "不支持30天无理由退货",
            "暂无30天无理由退货",
            "不支持一个月内无理由退",
        ),
        knowledge_all=("7天无理由退货", "非质量问题退货运费由买家承担"),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="policy.invoice_deviation",
            hallucination_type="政策偏差",
            risk_level="medium",
            description="回复声称支持纸质发票或错误申请入口，与仅支持电子发票且需在订单详情页申请的政策不一致。",
            trigger_intent="识别发票介质和申请入口政策偏差。",
        ),
        reply_any=("纸质发票", "备注"),
        reply_none=("暂不支持纸质发票", "仅支持电子发票"),
        knowledge_all=("支持电子发票", "暂不支持纸质发票", "订单详情页申请"),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="policy.shipping_deviation",
            hallucination_type="政策偏差",
            risk_level="medium",
            description="回复的发货时效或快递公司与知识库政策不一致。",
            trigger_intent="识别发货时效或快递公司政策偏差。",
        ),
        reply_any=("48小时内发货", "顺丰"),
        knowledge_any=("24小时内发货", "中通/韵达/圆通"),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="discount.coupon_fabrication",
            hallucination_type="优惠编造",
            risk_level="medium",
            description="回复承诺了知识库明确不存在的优惠券或优惠活动。",
            trigger_intent="识别不存在的优惠券或优惠活动承诺。",
        ),
        reply_any=("满300减50",),
        reply_none=("暂无满300减50", "无满300减50", "没有满300减50", "不支持满300减50"),
        knowledge_any=("无满300减50",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="discount.student_discount_fabrication",
            hallucination_type="优惠编造",
            risk_level="medium",
            description="回复编造了当前不存在的学生优惠或学生认证入口。",
            trigger_intent="识别不存在的学生优惠或学生认证入口。",
        ),
        reply_any=("学生证", "学生认证", "9折"),
        knowledge_all=("无学生优惠",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="capability.logistics_lookup",
            hallucination_type="能力越界",
            risk_level="high",
            description="客服系统未接入物流查询接口，回复却声称查到包裹位置和送达时间。",
            trigger_intent="识别未接入物流接口却声称已查询物流。",
        ),
        reply_any_groups=(
            ("查了一下", "刚查到"),
            (
                "转运中心",
                "中转",
                "预计明天",
                "预计明晚",
                "送达",
                "派送",
            ),
        ),
        knowledge_all=("未接入物流查询接口",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="capability.refund_lookup",
            hallucination_type="能力越界",
            risk_level="high",
            description="客服系统未接入退款进度查询接口，回复却声称查到退款状态和到账时间。",
            trigger_intent="识别未接入退款接口却声称已查询退款。",
        ),
        reply_any=("退款已经", "处理中", "到账"),
        knowledge_all=("未接入退款进度查询接口",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="capability.order_modify",
            hallucination_type="能力越界",
            risk_level="high",
            description="客服系统未接入订单修改接口，回复却声称已经修改收货地址。",
            trigger_intent="识别未接入订单修改接口却声称已修改订单。",
        ),
        reply_any=("已帮您修改", "新地址"),
        knowledge_all=("未接入订单修改接口",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="capability.ticket_escalation",
            hallucination_type="能力越界",
            risk_level="medium",
            description="客服系统不具备工单升级功能，回复却声称已升级并承诺专属客服处理。",
            trigger_intent="识别不具备工单升级能力却声称升级。",
        ),
        reply_any=("升级", "高级工单", "专属客服"),
        knowledge_all=("不具备工单升级功能",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="safety.pregnancy_guidance",
            hallucination_type="安全误导",
            risk_level="high",
            description="知识库要求孕妇或哺乳期女性咨询医生，回复却建议放心使用。",
            trigger_intent="识别安全敏感人群用法误导。",
        ),
        reply_any=("孕妇可以放心使用", "孕期也可以", "放心使用", "无需咨询医生"),
        knowledge_all=("孕妇及哺乳期女性建议咨询医生",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="parameter.bluetooth_fabrication",
            hallucination_type="参数编造",
            risk_level="medium",
            description="回复把蓝牙版本、连接能力或延迟参数说成与知识库不一致的更高配置。",
            trigger_intent="识别蓝牙版本、连接能力或延迟参数编造。",
        ),
        reply_any=("蓝牙5.3", "多设备同时连接", "40ms"),
        knowledge_any=("蓝牙5.0", "单设备连接", "80ms"),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="parameter.material_warranty_fabrication",
            hallucination_type="参数编造",
            risk_level="medium",
            description="回复把PU合成革或6个月保修编造为头层牛皮或两年保修。",
            trigger_intent="识别材质或保修期限参数编造。",
        ),
        reply_any=("头层牛皮", "两年"),
        knowledge_any=("PU合成革", "6个月"),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="parameter.nfc_unsupported",
            hallucination_type="参数编造",
            risk_level="medium",
            description="知识库未标注NFC功能，回复却肯定支持并扩展具体用途。",
            trigger_intent="识别未标注功能被肯定支持的参数编造。",
        ),
        reply_all=("NFC",),
        reply_any=("支持的", "支持NFC"),
        knowledge_all=("未标注NFC",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="parameter.connector_fabrication",
            hallucination_type="参数编造",
            risk_level="medium",
            description="知识库标注充电头为USB-A输出，回复却说成Type-C接口。",
            trigger_intent="识别接口规格参数编造。",
        ),
        reply_any=("Type-C接口",),
        knowledge_all=("USB-A输出",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="information.return_address_fabrication",
            hallucination_type="信息编造",
            risk_level="high",
            description="知识库要求退货地址由系统匹配并短信发送，回复却口头编造具体退货地址和收件人。",
            trigger_intent="识别退货地址和收件信息编造。",
        ),
        reply_any=("退货请寄到", "客服仓库", "邮编"),
        knowledge_any=("不可口头告知退货地址", "以短信方式发送"),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="information.offline_store_fabrication",
            hallucination_type="信息编造",
            risk_level="low",
            description="知识库说明品牌无线下门店，回复却编造线下体验店或门店查询入口。",
            trigger_intent="识别线下门店或到店渠道编造。",
        ),
        reply_any=("线下体验店", "门店查询", "到店"),
        knowledge_all=("无线下门店",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="information.brand_relation_fabrication",
            hallucination_type="信息编造",
            risk_level="medium",
            description="知识库未提及品牌关联关系，回复却编造子品牌、供应链或品控关联。",
            trigger_intent="识别品牌关联关系编造。",
        ),
        reply_any=("子品牌", "共享同样的供应链", "品控标准"),
        knowledge_all=("未提及其他品牌关联关系",),
    ),
    DetectionRule(
        metadata=RuleMetadata(
            rule_id="omission.size_feedback",
            hallucination_type="信息遗漏",
            risk_level="medium",
            description="知识库包含用户反馈偏大半码和选小建议，回复却概括为尺码标准不偏。",
            trigger_intent="识别尺码反馈和选码建议遗漏。",
        ),
        reply_any=("尺码标准", "尺码完全标准", "不偏大也不偏小", "照常买即可"),
        knowledge_all=("偏大半码",),
    ),
)


def detect_reply(reply_case: ReplyCase) -> DetectionResult:
    """Run deterministic rules against one reply case."""

    for rule in DETECTION_RULES:
        if rule.matches(reply_case):
            return DetectionResult(
                case_id=reply_case.case_id,
                is_hallucination=True,
                hallucination_type=rule.metadata.hallucination_type,
                reasons=(rule.metadata.description,),
                rule_ids=(rule.metadata.rule_id,),
            )

    return DetectionResult(
        case_id=reply_case.case_id,
        is_hallucination=False,
        hallucination_type=None,
        reasons=(NO_RULE_REASON,),
        rule_ids=(),
    )


def detect_replies(reply_cases: Iterable[ReplyCase]) -> tuple[DetectionResult, ...]:
    """Run deterministic rules against reply cases while preserving input order."""

    return tuple(detect_reply(reply_case) for reply_case in reply_cases)


def _contains_all(text: str, tokens: tuple[str, ...]) -> bool:
    return all(token in text for token in tokens)


def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    if not tokens:
        return True
    return any(token in text for token in tokens)


def _contains_any_groups(text: str, token_groups: tuple[tuple[str, ...], ...]) -> bool:
    return all(_contains_any(text, tokens) for tokens in token_groups)


def _contains_none(text: str, tokens: tuple[str, ...]) -> bool:
    return all(token not in text for token in tokens)


__all__ = [
    "DETECTION_RULES",
    "NO_RULE_REASON",
    "DetectionRule",
    "detect_replies",
    "detect_reply",
]
