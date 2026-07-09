from __future__ import annotations

import json
from pathlib import Path

import pytest

from customer_service_hallucination_audit.io import (
    DataValidationError,
    load_audit_dataset,
    load_ground_truth_labels,
    load_reply_cases,
)


def write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def valid_reply(case_id: str = "h01") -> dict[str, object]:
    return {
        "id": case_id,
        "user_question": "你们支持30天无理由退货吗？",
        "system_reply": "支持的，我们全品类支持30天无理由退货。",
        "knowledge_base": "普通商品支持7天无理由退货。",
    }


def valid_label(case_id: str = "h01") -> dict[str, object]:
    return {
        "id": case_id,
        "is_hallucination": True,
        "hallucination_type": "政策编造",
        "detail": "回复编造了更宽松的退货政策。",
    }


def test_load_audit_dataset_reads_default_data() -> None:
    dataset = load_audit_dataset(
        replies_path=Path("data/replies.json"),
        labels_path=Path("data/ground_truth.json"),
    )

    assert len(dataset.replies) == 20
    assert len(dataset.labels) == 20
    assert dataset.replies[0].case_id == "h01"
    assert dataset.labels[11].case_id == "h12"
    assert dataset.labels[11].is_hallucination is False
    assert dataset.labels[11].hallucination_type is None


def test_load_reply_cases_rejects_missing_required_field(tmp_path: Path) -> None:
    reply = valid_reply()
    del reply["knowledge_base"]
    path = write_json(tmp_path / "replies.json", [reply])

    with pytest.raises(DataValidationError, match="knowledge_base"):
        load_reply_cases(path)


def test_load_reply_cases_rejects_duplicate_ids(tmp_path: Path) -> None:
    path = write_json(tmp_path / "replies.json", [valid_reply("h01"), valid_reply("h01")])

    with pytest.raises(DataValidationError, match="Duplicate reply id 'h01'"):
        load_reply_cases(path)


def test_load_audit_dataset_rejects_id_mismatch(tmp_path: Path) -> None:
    replies_path = write_json(tmp_path / "replies.json", [valid_reply("h01")])
    labels_path = write_json(tmp_path / "ground_truth.json", [valid_label("h02")])

    with pytest.raises(DataValidationError, match="missing labels for: h01"):
        load_audit_dataset(replies_path, labels_path)


def test_load_ground_truth_labels_rejects_unknown_hallucination_type(tmp_path: Path) -> None:
    label = valid_label()
    label["hallucination_type"] = "未知类型"
    path = write_json(tmp_path / "ground_truth.json", [label])

    with pytest.raises(DataValidationError, match="Unknown hallucination_type '未知类型'"):
        load_ground_truth_labels(path)


def test_load_ground_truth_labels_rejects_non_hallucination_with_type(tmp_path: Path) -> None:
    label = valid_label()
    label["is_hallucination"] = False
    path = write_json(tmp_path / "ground_truth.json", [label])

    with pytest.raises(DataValidationError, match="must be null when is_hallucination is false"):
        load_ground_truth_labels(path)


def test_load_ground_truth_labels_rejects_hallucination_without_type(tmp_path: Path) -> None:
    label = valid_label()
    label["hallucination_type"] = None
    path = write_json(tmp_path / "ground_truth.json", [label])

    with pytest.raises(DataValidationError, match="must be set when is_hallucination is true"):
        load_ground_truth_labels(path)


def test_load_reply_cases_rejects_non_list_top_level(tmp_path: Path) -> None:
    path = write_json(tmp_path / "replies.json", {"id": "h01"})

    with pytest.raises(DataValidationError, match="must be a JSON array"):
        load_reply_cases(path)
