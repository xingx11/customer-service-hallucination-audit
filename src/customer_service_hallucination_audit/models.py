"""Domain models for the offline hallucination audit pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias, cast, get_args

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

HALLUCINATION_TYPES: tuple[HallucinationType, ...] = cast(
    tuple[HallucinationType, ...],
    get_args(HallucinationType),
)

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

    def __post_init__(self) -> None:
        _validate_hallucination_type_state(
            model_name="GroundTruthLabel",
            is_hallucination=self.is_hallucination,
            hallucination_type=self.hallucination_type,
        )


@dataclass(frozen=True)
class AuditDataset:
    """Validated reply cases paired with their human labels."""

    replies: tuple[ReplyCase, ...]
    labels: tuple[GroundTruthLabel, ...]


@dataclass(frozen=True)
class DetectionResult:
    """Detector output for one reply."""

    case_id: str
    is_hallucination: bool
    hallucination_type: HallucinationType | None
    reasons: tuple[str, ...]
    rule_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate_hallucination_type_state(
            model_name="DetectionResult",
            is_hallucination=self.is_hallucination,
            hallucination_type=self.hallucination_type,
        )


@dataclass(frozen=True)
class MetricsSummary:
    """Confusion-matrix counts and derived binary hallucination metrics."""

    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

    @property
    def total(self) -> int:
        return self.true_positive + self.false_positive + self.true_negative + self.false_negative

    @property
    def precision(self) -> float:
        return _safe_divide(self.true_positive, self.true_positive + self.false_positive)

    @property
    def recall(self) -> float:
        return _safe_divide(self.true_positive, self.true_positive + self.false_negative)

    @property
    def f1(self) -> float:
        if self.precision + self.recall == 0:
            return 0.0
        return 2 * self.precision * self.recall / (self.precision + self.recall)

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

    def __post_init__(self) -> None:
        if self.case_id != self.expected.case_id or self.case_id != self.predicted.case_id:
            raise ValueError("ErrorCase case_id must match expected and predicted case IDs")


def _validate_hallucination_type_state(
    *,
    model_name: str,
    is_hallucination: bool,
    hallucination_type: HallucinationType | None,
) -> None:
    if is_hallucination and hallucination_type is None:
        raise ValueError(
            f"{model_name} hallucination_type must be set when is_hallucination is true"
        )
    if not is_hallucination and hallucination_type is not None:
        raise ValueError(
            f"{model_name} hallucination_type must be None when is_hallucination is false"
        )


def _safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


__all__ = [
    "AuditDataset",
    "DetectionResult",
    "ErrorCase",
    "ErrorType",
    "GroundTruthLabel",
    "HALLUCINATION_TYPES",
    "HallucinationType",
    "MetricsSummary",
    "ReplyCase",
]
