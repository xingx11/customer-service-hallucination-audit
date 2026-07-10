"""Metrics and error analysis for hallucination detection results."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from customer_service_hallucination_audit.models import (
    HALLUCINATION_TYPES,
    DetectionResult,
    ErrorCase,
    ErrorType,
    GroundTruthLabel,
    HallucinationType,
    MetricsSummary,
    TypeMetricsSummary,
)
from customer_service_hallucination_audit.validation import (
    ensure_matching_ids,
    index_unique_by_id,
)


class MetricsValidationError(ValueError):
    """Raised when predictions and labels cannot be compared safely."""


def calculate_metrics(
    predictions: Iterable[DetectionResult],
    labels: Iterable[GroundTruthLabel],
) -> MetricsSummary:
    """Calculate binary hallucination detection metrics."""

    predictions_by_id, labels_by_id = _index_comparable_records(predictions, labels)
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    for case_id in sorted(labels_by_id):
        prediction = predictions_by_id[case_id]
        label = labels_by_id[case_id]

        if prediction.is_hallucination and label.is_hallucination:
            true_positive += 1
        elif prediction.is_hallucination and not label.is_hallucination:
            false_positive += 1
        elif not prediction.is_hallucination and label.is_hallucination:
            false_negative += 1
        else:
            true_negative += 1

    return MetricsSummary(
        true_positive=true_positive,
        false_positive=false_positive,
        true_negative=true_negative,
        false_negative=false_negative,
    )


def calculate_type_metrics(
    predictions: Iterable[DetectionResult],
    labels: Iterable[GroundTruthLabel],
) -> tuple[TypeMetricsSummary, ...]:
    """Calculate stable per-type counts for labels, predictions, and mismatches."""

    predictions_by_id, labels_by_id = _index_comparable_records(predictions, labels)
    label_counts: Counter[HallucinationType] = Counter()
    predicted_counts: Counter[HallucinationType] = Counter()
    true_positive_counts: Counter[HallucinationType] = Counter()
    mismatch_counts: Counter[HallucinationType] = Counter()

    for case_id in sorted(labels_by_id):
        prediction = predictions_by_id[case_id]
        label = labels_by_id[case_id]
        label_type = _positive_hallucination_type(label, record_name="label")
        prediction_type = _positive_hallucination_type(
            prediction,
            record_name="prediction",
        )

        if label_type is not None:
            label_counts[label_type] += 1
        if prediction_type is not None:
            predicted_counts[prediction_type] += 1

        if label_type is not None and label_type == prediction_type:
            true_positive_counts[label_type] += 1
            continue

        if label_type is not None:
            mismatch_counts[label_type] += 1
        if prediction_type is not None:
            mismatch_counts[prediction_type] += 1

    return tuple(
        TypeMetricsSummary(
            hallucination_type=hallucination_type,
            label_count=label_counts[hallucination_type],
            predicted_count=predicted_counts[hallucination_type],
            true_positive_count=true_positive_counts[hallucination_type],
            mismatch_count=mismatch_counts[hallucination_type],
        )
        for hallucination_type in HALLUCINATION_TYPES
    )


def analyze_errors(
    predictions: Iterable[DetectionResult],
    labels: Iterable[GroundTruthLabel],
) -> tuple[ErrorCase, ...]:
    """Return binary and type-level mismatches sorted by case ID."""

    predictions_by_id, labels_by_id = _index_comparable_records(predictions, labels)
    errors: list[ErrorCase] = []

    for case_id in sorted(labels_by_id):
        prediction = predictions_by_id[case_id]
        label = labels_by_id[case_id]
        error_type = _classify_error(prediction, label)
        if error_type is None:
            continue

        errors.append(
            ErrorCase(
                case_id=case_id,
                error_type=error_type,
                expected=label,
                predicted=prediction,
            )
        )

    return tuple(errors)


def select_error_cases(
    error_cases: Iterable[ErrorCase],
    error_type: ErrorType,
) -> tuple[ErrorCase, ...]:
    """Select error cases of one type while preserving their existing order."""

    return tuple(error_case for error_case in error_cases if error_case.error_type == error_type)


def _index_comparable_records(
    predictions: Iterable[DetectionResult],
    labels: Iterable[GroundTruthLabel],
) -> tuple[dict[str, DetectionResult], dict[str, GroundTruthLabel]]:
    predictions_by_id = _index_predictions(predictions)
    labels_by_id = _index_labels(labels)
    _ensure_matching_ids(predictions_by_id, labels_by_id)
    return predictions_by_id, labels_by_id


def _index_predictions(predictions: Iterable[DetectionResult]) -> dict[str, DetectionResult]:
    return index_unique_by_id(
        predictions,
        lambda prediction: prediction.case_id,
        record_name="prediction",
        exc_type=MetricsValidationError,
    )


def _index_labels(labels: Iterable[GroundTruthLabel]) -> dict[str, GroundTruthLabel]:
    return index_unique_by_id(
        labels,
        lambda label: label.case_id,
        record_name="label",
        exc_type=MetricsValidationError,
    )


def _ensure_matching_ids(
    predictions_by_id: dict[str, DetectionResult],
    labels_by_id: dict[str, GroundTruthLabel],
) -> None:
    ensure_matching_ids(
        set(labels_by_id),
        set(predictions_by_id),
        error_prefix="Prediction and label IDs must match",
        missing_actual_label="missing predictions for",
        unexpected_actual_label="unexpected predictions for",
        exc_type=MetricsValidationError,
    )


def _positive_hallucination_type(
    record: DetectionResult | GroundTruthLabel,
    *,
    record_name: str,
) -> HallucinationType | None:
    if not record.is_hallucination:
        return None

    hallucination_type = record.hallucination_type
    if hallucination_type is None:
        raise MetricsValidationError(
            f"{record_name} '{record.case_id}' hallucination_type must be set "
            "when is_hallucination is true"
        )
    if hallucination_type not in HALLUCINATION_TYPES:
        raise MetricsValidationError(
            f"Unknown hallucination_type '{hallucination_type}' for "
            f"{record_name} '{record.case_id}'"
        )
    return hallucination_type


def _classify_error(
    prediction: DetectionResult,
    label: GroundTruthLabel,
) -> ErrorType | None:
    if prediction.is_hallucination and not label.is_hallucination:
        return "false_positive"
    if not prediction.is_hallucination and label.is_hallucination:
        return "false_negative"
    if (
        prediction.is_hallucination
        and label.is_hallucination
        and prediction.hallucination_type != label.hallucination_type
    ):
        return "type_mismatch"
    return None


__all__ = [
    "MetricsValidationError",
    "analyze_errors",
    "calculate_metrics",
    "calculate_type_metrics",
    "select_error_cases",
]
