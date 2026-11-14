import json

import pytest

from document_batch_validator import DocumentBatchError
from document_ingestion import (
    load_document_batch,
    load_jsonl_batch,
    iter_jsonl_objects,
)


def test_json_loader_processing(tmp_path):
    path = tmp_path / "batch.json"

    documents = [
        {"title": " PYTHON ", "content": "One"},
        {"title": "python", "content": "One"},
        {"title": "RAG", "content": "Two"},
    ]

    path.write_text(json.dumps(documents), encoding="utf-8")

    report = load_document_batch(path)

    assert report["stats"] == {
        "total": 3,
        "unique": 2,
        "duplicates": 1,
    }


def test_json_loader_rejects_non_list(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text('{"title": "Python"}', encoding="utf-8")

    with pytest.raises(TypeError):
        load_document_batch(path)


def test_json_loader_invalid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_document_batch(path)


def test_json_loader_rejects_duplicates(tmp_path):
    path = tmp_path / "batch.json"

    documents = [
        {"title": "Python", "content": "One"},
        {"title": " PYTHON ", "content": "One"},
    ]

    path.write_text(json.dumps(documents), encoding="utf-8")

    with pytest.raises(DocumentBatchError):
        load_document_batch(path, reject_duplicates=True)


def test_jsonl_generator_defers_file_open(tmp_path):
    path = tmp_path / "created_later.jsonl"

    iterator = iter_jsonl_objects(path)

    assert not path.exists()

    path.write_text(
        '{"title": "Python", "content": "One"}\n',
        encoding="utf-8",
    )

    assert next(iterator)["title"] == "Python"

    iterator.close()


def test_jsonl_reader_skips_blank_lines(tmp_path):
    path = tmp_path / "batch.jsonl"

    path.write_text(
        '\n   \n{"title": "Python", "content": "One"}\n',
        encoding="utf-8",
    )

    records = list(iter_jsonl_objects(path))

    assert len(records) == 1
    assert records[0]["title"] == "Python"


def test_jsonl_reports_decode_error_and_cause(tmp_path):
    path = tmp_path / "broken.jsonl"

    path.write_text(
        '{"title": "A", "content": "One"}\n\nbroken\n',
        encoding="utf-8",
    )

    iterator = iter_jsonl_objects(path)

    assert next(iterator)["title"] == "A"

    with pytest.raises(
        ValueError,
        match="Invalid JSON on line 3",
    ) as exc:
        next(iterator)

    assert isinstance(
        exc.value.__cause__,
        json.JSONDecodeError,
    )

    assert list(iterator) == []


def test_jsonl_rejects_non_object(tmp_path):
    path = tmp_path / "batch.jsonl"
    path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(
        TypeError,
        match="Expected JSON object on line 1",
    ):
        list(iter_jsonl_objects(path))


def test_jsonl_skips_invalid_records(tmp_path):
    path = tmp_path / "batch.jsonl"

    path.write_text(
        '{"title": "A"}\n'
        'broken\n'
        '[]\n'
        '{"title": "B"}\n',
        encoding="utf-8",
    )

    records = list(
        iter_jsonl_objects(path, skip_invalid=True)
    )

    assert [record["title"] for record in records] == [
        "A",
        "B",
    ]


def test_jsonl_preserves_order(tmp_path):
    path = tmp_path / "batch.jsonl"

    path.write_text(
        '{"title": "RAG"}\n'
        '{"title": "Python"}\n',
        encoding="utf-8",
    )

    records = list(iter_jsonl_objects(path))

    assert [record["title"] for record in records] == [
        "RAG",
        "Python",
    ]


@pytest.mark.parametrize("invalid_path", [None, 123])
def test_jsonl_rejects_invalid_path_immediately(invalid_path):
    with pytest.raises(TypeError):
        iter_jsonl_objects(invalid_path)


@pytest.mark.parametrize("invalid_flag", [None, 1])
def test_jsonl_rejects_invalid_flag_immediately(invalid_flag):
    with pytest.raises(TypeError):
        iter_jsonl_objects("batch.jsonl", skip_invalid=invalid_flag)


def test_jsonl_loader_statistics(tmp_path):
    path = tmp_path / "batch.jsonl"

    path.write_text(
        '{"title": " PYTHON ", "content": "One"}\n'
        '{"title": "python", "content": "One"}\n'
        '{"title": "RAG", "content": "Two"}\n',
        encoding="utf-8",
    )

    report = load_jsonl_batch(path)

    assert report["stats"] == {
        "total": 3,
        "unique": 2,
        "duplicates": 1,
    }

    assert [doc["title"] for doc in report["documents"]] == [
        "python",
        "rag",
    ]


def test_jsonl_loader_rejects_duplicates(tmp_path):
    path = tmp_path / "batch.jsonl"

    path.write_text(
        '{"title": "Python", "content": "One"}\n'
        '{"title": " PYTHON ", "content": "One"}\n',
        encoding="utf-8",
    )

    with pytest.raises(
        DocumentBatchError,
        match="Duplicate documents are not allowed",
    ):
        load_jsonl_batch(path, reject_duplicates=True)


def test_jsonl_loader_skip_invalid_statistics(tmp_path):
    path = tmp_path / "batch.jsonl"

    path.write_text(
        '{"title": "A", "content": "One"}\n'
        'broken\n'
        '[]\n'
        '{"title": "B", "content": "Two"}\n',
        encoding="utf-8",
    )

    report = load_jsonl_batch(path, skip_invalid=True)

    assert report["stats"] == {
        "total": 2,
        "unique": 2,
        "duplicates": 0,
    }


def test_jsonl_loader_invalid_document(tmp_path):
    path = tmp_path / "batch.jsonl"

    path.write_text(
        '{"title": "A", "content": 10}\n',
        encoding="utf-8",
    )

    with pytest.raises(DocumentBatchError):
        load_jsonl_batch(path)