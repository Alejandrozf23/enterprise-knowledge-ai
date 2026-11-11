from dataclasses import FrozenInstanceError
from copy import deepcopy

import pytest

from document_models import (
    NormalizedDocument,
    build_document_records,
)
from document_batch_validator import DocumentBatchError


def test_build_records_normalizes_and_deduplicates():
    documents = [
        {"title": " PYTHON ", "content": " One two "},
        {"title": "python", "content": "One two"},
        {"title": "RAG", "content": "Three"},
    ]

    report = build_document_records(documents)

    assert report["stats"] == {
        "total": 3,
        "unique": 2,
        "duplicates": 1,
    }

    assert report["documents"] == [
        NormalizedDocument("python", "One two", 2),
        NormalizedDocument("rag", "Three", 1),
    ]


def test_empty_collection():
    assert build_document_records([]) == {
        "documents": [],
        "stats": {
            "total": 0,
            "unique": 0,
            "duplicates": 0,
        },
    }


def test_original_documents_are_not_modified():
    documents = [
        {"title": " Python ", "content": " One two "}
    ]

    original = deepcopy(documents)

    build_document_records(documents)

    assert documents == original


def test_duplicate_rejection_uses_existing_policy():
    documents = [
        {"title": "Python", "content": "One"},
        {"title": " PYTHON ", "content": "One"},
    ]

    with pytest.raises(
        DocumentBatchError,
        match="Duplicate documents are not allowed",
    ):
        build_document_records(
            documents,
            reject_duplicates=True,
        )


def test_invalid_collection_uses_domain_exception():
    with pytest.raises(DocumentBatchError):
        build_document_records(None)


def test_invalid_option_propagates_type_error():
    with pytest.raises(TypeError):
        build_document_records(
            [],
            reject_duplicates=1,
        )


def test_frozen_model_rejects_assignment():
    document = NormalizedDocument("python", "One", 1)

    with pytest.raises(FrozenInstanceError):
        document.title = "java"


def test_equality_and_hashability():
    first = NormalizedDocument("python", "One", 1)
    second = NormalizedDocument("python", "One", 1)

    assert first == second
    assert first is not second
    assert len({first, second}) == 1


def test_to_dict_returns_independent_dictionary():
    document = NormalizedDocument("python", "One", 1)

    snapshot = document.to_dict()
    snapshot["title"] = "modified"

    assert document.title == "python"
    assert document.to_dict()["title"] == "python"


@pytest.mark.parametrize(
    "field,value,expected_error",
    [
        ("title", " PYTHON ", ValueError),
        ("content", " one ", ValueError),
        ("word_count", 2, ValueError),
        ("word_count", True, TypeError),
        ("title", 123, TypeError),
        ("content", None, TypeError),
    ],
)
def test_invalid_direct_construction(
    field,
    value,
    expected_error,
):
    values = {
        "title": "python",
        "content": "one",
        "word_count": 1,
    }

    values[field] = value

    with pytest.raises(expected_error):
        NormalizedDocument(**values)