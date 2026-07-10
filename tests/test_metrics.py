from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import cast

import pytest

from customer_service_hallucination_audit.metrics import (
    MetricsValidationError,
    analyze_errors,
    calculate_metrics,
    calculate_type_metrics,
    select_error_cases,
)
from customer_service_hallucination_audit.models import (
    HALLUCINATION_TYPES,
    DetectionResult,
    ErrorType,
    GroundTruthLabel,
    HallucinationType,
    TypeMetricsSummary,
)


def label(
    case_id: str,
    *,
    is_hallucination: bool,
    hallucination_type: HallucinationType | None = None,
) -> GroundTruthLabel:
    return GroundTruthLabel(
        case_id=case_id,
        is_hallucination=is_hallucination,
        hallucination_type=hallucination_type,
        detail="人工标注说明",
    )


def result(
    case_id: str,
    *,
    is_hallucination: bool,
    hallucination_type: HallucinationType | None = None,
) -> DetectionResult:
    return DetectionResult(
        case_id=case_id,
        is_hallucination=is_hallucination,
        hallucination_type=hallucination_type,
        reasons=("检测原因",),
        rule_ids=("test.rule",) if is_hallucination else (),
    )


class ExhaustionTracker:
    def __init__(self) -> None:
        self.is_exhausted = False


class ExhaustionAwareRecord:
    def __init__(
        self,
        case_id: str,
        *,
        is_hallucination: bool,
        exhaustion_tracker: ExhaustionTracker,
    ) -> None:
        self._case_id = case_id
        self.is_hallucination = is_hallucination
        self.hallucination_type = None
        self.exhaustion_tracker = exhaustion_tracker

    @property
    def case_id(self) -> str:
        if self.exhaustion_tracker.is_exhausted:
            raise AssertionError("case_id was read after the source iterable was exhausted")
        return self._case_id


class ExhaustionAwareIterable:
    def __init__(
        self,
        records: tuple[ExhaustionAwareRecord, ...],
        *,
        exhaustion_tracker: ExhaustionTracker,
    ) -> None:
        self.records = records
        self.exhaustion_tracker = exhaustion_tracker

    def __iter__(self) -> Iterator[ExhaustionAwareRecord]:
        yield from self.records
        self.exhaustion_tracker.is_exhausted = True


def test_calculate_metrics_counts_binary_outcomes_and_rates() -> None:
    labels = (
        label("h01", is_hallucination=True, hallucination_type="政策编造"),
        label("h02", is_hallucination=False),
        label("h03", is_hallucination=True, hallucination_type="信息遗漏"),
        label("h04", is_hallucination=False),
        label("h05", is_hallucination=True, hallucination_type="参数编造"),
    )
    predictions = (
        result("h01", is_hallucination=True, hallucination_type="政策编造"),
        result("h02", is_hallucination=True, hallucination_type="优惠编造"),
        result("h03", is_hallucination=False),
        result("h04", is_hallucination=False),
        result("h05", is_hallucination=True, hallucination_type="信息编造"),
    )

    summary = calculate_metrics(predictions, labels)

    assert summary.true_positive == 2
    assert summary.false_positive == 1
    assert summary.true_negative == 1
    assert summary.false_negative == 1
    assert summary.precision == pytest.approx(2 / 3)
    assert summary.recall == pytest.approx(2 / 3)
    assert summary.f1 == pytest.approx(2 / 3)
    assert summary.accuracy == pytest.approx(3 / 5)


def test_calculate_metrics_indexes_streaming_iterables_before_exhaustion() -> None:
    prediction_tracker = ExhaustionTracker()
    label_tracker = ExhaustionTracker()
    predictions = ExhaustionAwareIterable(
        (
            ExhaustionAwareRecord(
                "h01",
                is_hallucination=False,
                exhaustion_tracker=prediction_tracker,
            ),
        ),
        exhaustion_tracker=prediction_tracker,
    )
    labels = ExhaustionAwareIterable(
        (
            ExhaustionAwareRecord(
                "h01",
                is_hallucination=False,
                exhaustion_tracker=label_tracker,
            ),
        ),
        exhaustion_tracker=label_tracker,
    )

    summary = calculate_metrics(
        cast(Iterable[DetectionResult], predictions),
        cast(Iterable[GroundTruthLabel], labels),
    )

    assert summary.true_negative == 1
    assert summary.total == 1


def test_analyze_errors_distinguishes_binary_and_type_errors() -> None:
    labels = (
        label("h01", is_hallucination=True, hallucination_type="政策编造"),
        label("h02", is_hallucination=False),
        label("h03", is_hallucination=True, hallucination_type="信息遗漏"),
        label("h04", is_hallucination=False),
        label("h05", is_hallucination=True, hallucination_type="参数编造"),
    )
    predictions = (
        result("h01", is_hallucination=True, hallucination_type="政策编造"),
        result("h02", is_hallucination=True, hallucination_type="优惠编造"),
        result("h03", is_hallucination=False),
        result("h04", is_hallucination=False),
        result("h05", is_hallucination=True, hallucination_type="信息编造"),
    )

    errors = analyze_errors(predictions, labels)

    assert tuple(error.case_id for error in errors) == ("h02", "h03", "h05")
    assert tuple(error.error_type for error in errors) == (
        "false_positive",
        "false_negative",
        "type_mismatch",
    )
    assert tuple(error.case_id for error in select_error_cases(errors, "false_positive")) == (
        "h02",
    )
    assert tuple(error.case_id for error in select_error_cases(errors, "false_negative")) == (
        "h03",
    )
    assert tuple(error.case_id for error in select_error_cases(errors, "type_mismatch")) == ("h05",)


def test_analyze_errors_sorts_errors_by_case_id() -> None:
    labels = (
        label("h20", is_hallucination=True, hallucination_type="能力越界"),
        label("h02", is_hallucination=False),
        label("h11", is_hallucination=True, hallucination_type="参数编造"),
    )
    predictions = (
        result("h20", is_hallucination=False),
        result("h02", is_hallucination=True, hallucination_type="安全误导"),
        result("h11", is_hallucination=True, hallucination_type="信息编造"),
    )

    errors = analyze_errors(predictions, labels)

    assert tuple(error.case_id for error in errors) == ("h02", "h11", "h20")
    assert tuple(error.error_type for error in errors) == (
        "false_positive",
        "type_mismatch",
        "false_negative",
    )


def test_calculate_metrics_returns_zero_rates_for_empty_input() -> None:
    summary = calculate_metrics((), ())

    assert summary.true_positive == 0
    assert summary.false_positive == 0
    assert summary.true_negative == 0
    assert summary.false_negative == 0
    assert summary.precision == 0.0
    assert summary.recall == 0.0
    assert summary.f1 == 0.0
    assert summary.accuracy == 0.0


def test_calculate_metrics_handles_all_positive_input() -> None:
    labels = (
        label("h01", is_hallucination=True, hallucination_type="政策编造"),
        label("h02", is_hallucination=True, hallucination_type="信息遗漏"),
    )
    predictions = (
        result("h01", is_hallucination=True, hallucination_type="政策编造"),
        result("h02", is_hallucination=False),
    )

    summary = calculate_metrics(predictions, labels)

    assert summary.true_positive == 1
    assert summary.false_positive == 0
    assert summary.true_negative == 0
    assert summary.false_negative == 1
    assert summary.precision == 1.0
    assert summary.recall == 0.5
    assert summary.f1 == pytest.approx(2 / 3)


def test_calculate_metrics_handles_all_negative_input() -> None:
    labels = (
        label("h01", is_hallucination=False),
        label("h02", is_hallucination=False),
    )
    predictions = (
        result("h01", is_hallucination=False),
        result("h02", is_hallucination=True, hallucination_type="优惠编造"),
    )

    summary = calculate_metrics(predictions, labels)

    assert summary.true_positive == 0
    assert summary.false_positive == 1
    assert summary.true_negative == 1
    assert summary.false_negative == 0
    assert summary.precision == 0.0
    assert summary.recall == 0.0
    assert summary.f1 == 0.0


def test_calculate_metrics_handles_no_predicted_positives() -> None:
    labels = (
        label("h01", is_hallucination=True, hallucination_type="政策编造"),
        label("h02", is_hallucination=False),
    )
    predictions = (
        result("h01", is_hallucination=False),
        result("h02", is_hallucination=False),
    )

    summary = calculate_metrics(predictions, labels)

    assert summary.true_positive == 0
    assert summary.false_positive == 0
    assert summary.true_negative == 1
    assert summary.false_negative == 1
    assert summary.precision == 0.0
    assert summary.recall == 0.0
    assert summary.f1 == 0.0


def test_calculate_type_metrics_counts_labels_predictions_true_positives_and_mismatches() -> None:
    labels = (
        label("h01", is_hallucination=True, hallucination_type="政策编造"),
        label("h02", is_hallucination=True, hallucination_type="信息遗漏"),
        label("h03", is_hallucination=False),
        label("h04", is_hallucination=True, hallucination_type="参数编造"),
        label("h05", is_hallucination=False),
    )
    predictions = (
        result("h01", is_hallucination=True, hallucination_type="政策编造"),
        result("h02", is_hallucination=False),
        result("h03", is_hallucination=True, hallucination_type="优惠编造"),
        result("h04", is_hallucination=True, hallucination_type="信息编造"),
        result("h05", is_hallucination=False),
    )

    summaries = calculate_type_metrics(predictions, labels)

    assert tuple(summary.hallucination_type for summary in summaries) == HALLUCINATION_TYPES
    summaries_by_type = {summary.hallucination_type: summary for summary in summaries}
    assert summaries_by_type["政策编造"] == TypeMetricsSummary(
        hallucination_type="政策编造",
        label_count=1,
        predicted_count=1,
        true_positive_count=1,
        mismatch_count=0,
    )
    assert summaries_by_type["信息遗漏"] == TypeMetricsSummary(
        hallucination_type="信息遗漏",
        label_count=1,
        predicted_count=0,
        true_positive_count=0,
        mismatch_count=1,
    )
    assert summaries_by_type["优惠编造"] == TypeMetricsSummary(
        hallucination_type="优惠编造",
        label_count=0,
        predicted_count=1,
        true_positive_count=0,
        mismatch_count=1,
    )
    assert summaries_by_type["参数编造"] == TypeMetricsSummary(
        hallucination_type="参数编造",
        label_count=1,
        predicted_count=0,
        true_positive_count=0,
        mismatch_count=1,
    )
    assert summaries_by_type["信息编造"] == TypeMetricsSummary(
        hallucination_type="信息编造",
        label_count=0,
        predicted_count=1,
        true_positive_count=0,
        mismatch_count=1,
    )


def test_calculate_type_metrics_returns_all_known_types_for_empty_input() -> None:
    summaries = calculate_type_metrics((), ())

    assert tuple(summary.hallucination_type for summary in summaries) == HALLUCINATION_TYPES
    assert all(summary.label_count == 0 for summary in summaries)
    assert all(summary.predicted_count == 0 for summary in summaries)
    assert all(summary.true_positive_count == 0 for summary in summaries)
    assert all(summary.mismatch_count == 0 for summary in summaries)


def test_calculate_type_metrics_handles_no_predicted_positives() -> None:
    labels = (
        label("h01", is_hallucination=True, hallucination_type="政策编造"),
        label("h02", is_hallucination=False),
    )
    predictions = (
        result("h01", is_hallucination=False),
        result("h02", is_hallucination=False),
    )

    summaries = calculate_type_metrics(predictions, labels)

    summaries_by_type = {summary.hallucination_type: summary for summary in summaries}
    assert summaries_by_type["政策编造"] == TypeMetricsSummary(
        hallucination_type="政策编造",
        label_count=1,
        predicted_count=0,
        true_positive_count=0,
        mismatch_count=1,
    )
    assert all(
        summary
        == TypeMetricsSummary(
            hallucination_type=summary.hallucination_type,
            label_count=0,
            predicted_count=0,
            true_positive_count=0,
            mismatch_count=0,
        )
        for summary in summaries
        if summary.hallucination_type != "政策编造"
    )


def test_calculate_type_metrics_rejects_unknown_hallucination_type() -> None:
    labels = (
        label(
            "h01",
            is_hallucination=True,
            hallucination_type=cast(HallucinationType, "未知类型"),
        ),
    )
    predictions = (result("h01", is_hallucination=False),)

    with pytest.raises(MetricsValidationError, match="Unknown hallucination_type '未知类型'"):
        calculate_type_metrics(predictions, labels)


def test_calculate_type_metrics_reuses_comparable_record_validation() -> None:
    labels = (label("h01", is_hallucination=False),)
    predictions = (result("h02", is_hallucination=False),)

    with pytest.raises(MetricsValidationError, match="Prediction and label IDs must match"):
        calculate_type_metrics(predictions, labels)


def test_metrics_rejects_mismatched_case_ids() -> None:
    labels = (label("h01", is_hallucination=False),)
    predictions = (result("h02", is_hallucination=False),)

    with pytest.raises(MetricsValidationError, match="Prediction and label IDs must match"):
        calculate_metrics(predictions, labels)


def test_metrics_rejects_duplicate_ids() -> None:
    labels = (
        label("h01", is_hallucination=False),
        label("h01", is_hallucination=False),
    )
    predictions = (result("h01", is_hallucination=False),)

    with pytest.raises(MetricsValidationError, match="Duplicate label id 'h01'"):
        analyze_errors(predictions, labels)


@pytest.mark.parametrize("error_type", ("false_positive", "false_negative", "type_mismatch"))
def test_select_error_cases_returns_empty_tuple_when_type_is_absent(error_type: ErrorType) -> None:
    assert select_error_cases((), error_type) == ()
