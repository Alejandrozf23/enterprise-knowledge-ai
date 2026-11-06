from copy import deepcopy

import pytest

import document_batch_validator as validator_module

from document_batch_validator import (
    DocumentBatchError,
    validate_document_batch,
)


def test_valid_batch():
    documents = [
        {"title": " Python ", "content": " Basics "}
    ]

    result = validate_document_batch(documents)

    assert result["stats"] == {
        "total": 1,
        "unique": 1,
        "duplicates": 0,
    }
    assert result["documents"][0]["title"] == "python"
    assert result["documents"][0]["content"] == "Basics"


def test_duplicates_allowed_by_default():
    documents = [
        {"title": "Python", "content": "Basics"},
        {"title": " PYTHON ", "content": "Basics"},
    ]

    result = validate_document_batch(documents)

    assert result["stats"]["duplicates"] == 1
    assert len(result["documents"]) == 1


def test_rejects_normalized_duplicates():
    documents = [
        {"title": "Python", "content": "Basics"},
        {"title": " PYTHON ", "content": " Basics "},
    ]

    with pytest.raises(
        DocumentBatchError,
        match="Duplicate documents are not allowed",
    ):
        validate_document_batch(
            documents,
            reject_duplicates=True,
        )


def test_allows_same_title_with_different_content():
    documents = [
        {"title": "Python", "content": "Basics"},
        {"title": "PYTHON", "content": "Advanced"},
    ]

    result = validate_document_batch(
        documents,
        reject_duplicates=True,
    )

    assert result["stats"]["unique"] == 2


def test_empty_batch():
    result = validate_document_batch(
        [],
        reject_duplicates=True,
    )

    assert result["documents"] == []
    assert result["stats"] == {
        "total": 0,
        "unique": 0,
        "duplicates": 0,
    }


def test_does_not_mutate_input():
    documents = [
        {"title": " Python ", "content": " Basics "}
    ]
    original = deepcopy(documents)

    result = validate_document_batch(documents)
    result["documents"][0]["title"] = "changed"

    assert documents == original


@pytest.mark.parametrize(
    "invalid_flag",
    [None, 0, 1, "true"],
)
def test_invalid_reject_duplicates_type(invalid_flag):
    with pytest.raises(TypeError):
        validate_document_batch(
            [],
            reject_duplicates=invalid_flag,
        )


@pytest.mark.parametrize(
    "invalid_documents",
    [None, "invalid", [123]],
)
def test_invalid_collection_is_wrapped(invalid_documents):
    with pytest.raises(DocumentBatchError) as exc:
        validate_document_batch(invalid_documents)

    assert str(exc.value) == "Invalid document collection"
    assert isinstance(exc.value.__cause__, TypeError)


@pytest.mark.parametrize(
    "error_type",
    [TypeError, ValueError, KeyError],
)
def test_preserves_known_error_cause(
    monkeypatch,
    error_type,
):
    def failing_processor(documents):
        raise error_type("broken")

    monkeypatch.setattr(
        validator_module,
        "process_document_collection_with_stats",
        failing_processor,
    )

    with pytest.raises(DocumentBatchError) as exc:
        validator_module.validate_document_batch([])

    assert type(exc.value.__cause__) is error_type


def test_unexpected_exception_propagates(monkeypatch):
    def failing_processor(documents):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(
        validator_module,
        "process_document_collection_with_stats",
        failing_processor,
    )

    with pytest.raises(RuntimeError, match="unexpected"):
        validator_module.validate_document_batch([])