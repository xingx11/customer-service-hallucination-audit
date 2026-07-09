"""Shared validation helpers for audit data boundaries."""

from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Set as AbstractSet


def ensure_unique_ids(
    case_ids: Iterable[str],
    *,
    record_name: str,
    exc_type: type[ValueError],
) -> None:
    """Ensure IDs are unique while preserving caller-specific error types."""

    seen: set[str] = set()
    for case_id in case_ids:
        if case_id in seen:
            raise exc_type(f"Duplicate {record_name} id '{case_id}'")
        seen.add(case_id)


def ensure_matching_ids(
    expected_ids: AbstractSet[str],
    actual_ids: AbstractSet[str],
    *,
    error_prefix: str,
    missing_actual_label: str,
    unexpected_actual_label: str,
    exc_type: type[ValueError],
) -> None:
    """Ensure two ID sets match with caller-specific labels and error types."""

    if expected_ids == actual_ids:
        return

    details: list[str] = []
    missing_actual = sorted(expected_ids - actual_ids)
    unexpected_actual = sorted(actual_ids - expected_ids)
    if missing_actual:
        details.append(f"{missing_actual_label}: {', '.join(missing_actual)}")
    if unexpected_actual:
        details.append(f"{unexpected_actual_label}: {', '.join(unexpected_actual)}")

    raise exc_type(error_prefix + "; " + "; ".join(details))


__all__ = [
    "ensure_matching_ids",
    "ensure_unique_ids",
]
