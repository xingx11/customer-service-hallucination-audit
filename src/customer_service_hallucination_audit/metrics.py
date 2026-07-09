"""Metrics and error analysis for hallucination detection results."""

from __future__ import annotations

from collections.abc import Iterable

from customer_service_hallucination_audit.models import (
    DetectionResult,
    ErrorCase,
    ErrorType,
    GroundTruthLabel,
    MetricsSummary,
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

    precision = _safe_divide(true_positive, true_positive + false_positive)
    recall = _safe_divide(true_positive, true_positive + false_negative)
    return MetricsSummary(
        true_positive=true_positive,
        false_positive=false_positive,
        true_negative=true_negative,
        false_negative=false_negative,
        precision=precision,
        recall=recall,
        f1=_calculate_f1(precision, recall),
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
    predictions_by_id: dict[str, DetectionResult] = {}
    for prediction in predictions:
        if prediction.case_id in predictions_by_id:
            raise MetricsValidationError(f"Duplicate prediction id '{prediction.case_id}'")
        predictions_by_id[prediction.case_id] = prediction
    return predictions_by_id


def _index_labels(labels: Iterable[GroundTruthLabel]) -> dict[str, GroundTruthLabel]:
    labels_by_id: dict[str, GroundTruthLabel] = {}
    for label in labels:
        if label.case_id in labels_by_id:
            raise MetricsValidationError(f"Duplicate label id '{label.case_id}'")
        labels_by_id[label.case_id] = label
    return labels_by_id


def _ensure_matching_ids(
    predictions_by_id: dict[str, DetectionResult],
    labels_by_id: dict[str, GroundTruthLabel],
) -> None:
    prediction_ids = set(predictions_by_id)
    label_ids = set(labels_by_id)
    if prediction_ids == label_ids:
        return

    details: list[str] = []
    missing_predictions = sorted(label_ids - prediction_ids)
    unexpected_predictions = sorted(prediction_ids - label_ids)
    if missing_predictions:
        details.append(f"missing predictions for: {', '.join(missing_predictions)}")
    if unexpected_predictions:
        details.append(f"unexpected predictions for: {', '.join(unexpected_predictions)}")

    raise MetricsValidationError("Prediction and label IDs must match; " + "; ".join(details))


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


def _safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _calculate_f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


__all__ = [
    "MetricsValidationError",
    "analyze_errors",
    "calculate_metrics",
    "select_error_cases",
]
