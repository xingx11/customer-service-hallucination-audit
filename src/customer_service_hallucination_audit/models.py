"""Domain models for the offline hallucination audit pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

HallucinationType: TypeAlias = Literal[
    "政策编造",
    "政策偏差",
    "参数编造",
    "优惠编造",
    "信息编造",
    "能力越界",
    "安全误导",
    "信息遗漏",
]

ErrorType: TypeAlias = Literal["false_positive", "false_negative", "type_mismatch"]


@dataclass(frozen=True)
class ReplyCase:
    """One customer-service reply and the knowledge-base evidence available to audit it."""

    case_id: str
    user_question: str
    system_reply: str
    knowledge_base: str


@dataclass(frozen=True)
class GroundTruthLabel:
    """Human label used only for evaluation, never for detector prediction."""

    case_id: str
    is_hallucination: bool
    hallucination_type: HallucinationType | None
    detail: str


@dataclass(frozen=True)
class DetectionResult:
    """Detector output for one reply."""

    case_id: str
    is_hallucination: bool
    hallucination_type: HallucinationType | None
    reasons: tuple[str, ...]
    rule_ids: tuple[str, ...]


@dataclass(frozen=True)
class MetricsSummary:
    """Confusion-matrix counts and derived binary hallucination metrics."""

    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    precision: float
    recall: float
    f1: float

    @property
    def total(self) -> int:
        return self.true_positive + self.false_positive + self.true_negative + self.false_negative

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.true_positive + self.true_negative) / self.total


@dataclass(frozen=True)
class ErrorCase:
    """A mismatch between a detector result and the human label."""

    case_id: str
    error_type: ErrorType
    expected: GroundTruthLabel
    predicted: DetectionResult


__all__ = [
    "DetectionResult",
    "ErrorCase",
    "ErrorType",
    "GroundTruthLabel",
    "HallucinationType",
    "MetricsSummary",
    "ReplyCase",
]
