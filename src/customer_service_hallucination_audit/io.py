"""JSON loading and boundary validation for audit data."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from json import JSONDecodeError
from pathlib import Path
from typing import cast

from customer_service_hallucination_audit.models import (
    HALLUCINATION_TYPES,
    AuditDataset,
    GroundTruthLabel,
    HallucinationType,
    ReplyCase,
)


class DataValidationError(ValueError):
    """Raised when input JSON cannot be converted into a valid audit dataset."""


def load_reply_cases(path: Path) -> tuple[ReplyCase, ...]:
    """Load and validate customer service reply cases from a JSON file."""

    items = _require_array(_read_json(path), context=str(path))
    replies = tuple(_parse_reply_case(item, index=index) for index, item in enumerate(items))
    _ensure_unique_case_ids((reply.case_id for reply in replies), record_name="reply")
    return replies


def load_ground_truth_labels(path: Path) -> tuple[GroundTruthLabel, ...]:
    """Load and validate human ground-truth labels from a JSON file."""

    items = _require_array(_read_json(path), context=str(path))
    labels = tuple(_parse_ground_truth_label(item, index=index) for index, item in enumerate(items))
    _ensure_unique_case_ids((label.case_id for label in labels), record_name="ground truth")
    return labels


def load_audit_dataset(replies_path: Path, labels_path: Path) -> AuditDataset:
    """Load replies and labels, then verify both files describe the same case IDs."""

    replies = load_reply_cases(replies_path)
    labels = load_ground_truth_labels(labels_path)
    _ensure_matching_case_ids(replies, labels)
    return AuditDataset(replies=replies, labels=labels)


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DataValidationError(f"Cannot read JSON file {path}: {exc}") from exc
    except UnicodeError as exc:
        raise DataValidationError(f"Cannot decode JSON file {path} as UTF-8: {exc}") from exc
    except JSONDecodeError as exc:
        raise DataValidationError(f"Invalid JSON in {path}: {exc.msg}") from exc


def _parse_reply_case(value: object, *, index: int) -> ReplyCase:
    context = f"reply item {index}"
    record = _require_object(value, context=context)
    return ReplyCase(
        case_id=_require_str(record, "id", context=context),
        user_question=_require_str(record, "user_question", context=context),
        system_reply=_require_str(record, "system_reply", context=context),
        knowledge_base=_require_str(record, "knowledge_base", context=context),
    )


def _parse_ground_truth_label(value: object, *, index: int) -> GroundTruthLabel:
    context = f"ground truth item {index}"
    record = _require_object(value, context=context)
    is_hallucination = _require_bool(record, "is_hallucination", context=context)
    hallucination_type = _require_hallucination_type(record, context=context)

    if is_hallucination and hallucination_type is None:
        raise DataValidationError(
            f"{context} field 'hallucination_type' must be set when is_hallucination is true"
        )
    if not is_hallucination and hallucination_type is not None:
        raise DataValidationError(
            f"{context} field 'hallucination_type' must be null when is_hallucination is false"
        )

    return GroundTruthLabel(
        case_id=_require_str(record, "id", context=context),
        is_hallucination=is_hallucination,
        hallucination_type=hallucination_type,
        detail=_require_str(record, "detail", context=context),
    )


def _require_array(value: object, *, context: str) -> list[object]:
    if not isinstance(value, list):
        raise DataValidationError(f"{context} must be a JSON array")
    return cast(list[object], value)


def _require_object(value: object, *, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise DataValidationError(f"{context} must be a JSON object")

    for key in value:
        if not isinstance(key, str):
            raise DataValidationError(f"{context} must use string field names")

    return cast(Mapping[str, object], value)


def _require_field(record: Mapping[str, object], field_name: str, *, context: str) -> object:
    try:
        return record[field_name]
    except KeyError as exc:
        raise DataValidationError(f"{context} missing required field '{field_name}'") from exc


def _require_str(record: Mapping[str, object], field_name: str, *, context: str) -> str:
    value = _require_field(record, field_name, context=context)
    if not isinstance(value, str):
        raise DataValidationError(f"{context} field '{field_name}' must be a string")
    return value


def _require_bool(record: Mapping[str, object], field_name: str, *, context: str) -> bool:
    value = _require_field(record, field_name, context=context)
    if not isinstance(value, bool):
        raise DataValidationError(f"{context} field '{field_name}' must be a boolean")
    return value


def _require_hallucination_type(
    record: Mapping[str, object],
    *,
    context: str,
) -> HallucinationType | None:
    value = _require_field(record, "hallucination_type", context=context)
    if value is None:
        return None

    if not isinstance(value, str):
        raise DataValidationError(f"{context} field 'hallucination_type' must be a string or null")

    if value not in HALLUCINATION_TYPES:
        raise DataValidationError(f"Unknown hallucination_type '{value}' in {context}")

    return value


def _ensure_unique_case_ids(case_ids: Iterable[str], *, record_name: str) -> None:
    seen: set[str] = set()
    for case_id in case_ids:
        if case_id in seen:
            raise DataValidationError(f"Duplicate {record_name} id '{case_id}'")
        seen.add(case_id)


def _ensure_matching_case_ids(
    replies: tuple[ReplyCase, ...],
    labels: tuple[GroundTruthLabel, ...],
) -> None:
    reply_ids = {reply.case_id for reply in replies}
    label_ids = {label.case_id for label in labels}
    if reply_ids == label_ids:
        return

    details: list[str] = []
    missing_labels = sorted(reply_ids - label_ids)
    unexpected_labels = sorted(label_ids - reply_ids)
    if missing_labels:
        details.append(f"missing labels for: {', '.join(missing_labels)}")
    if unexpected_labels:
        details.append(f"unexpected labels for: {', '.join(unexpected_labels)}")

    raise DataValidationError("Reply and ground truth IDs must match; " + "; ".join(details))
