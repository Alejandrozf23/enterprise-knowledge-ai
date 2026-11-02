from copy import deepcopy

import pytest

from document_collection_processor import (
    process_document_collection,
    process_document_collection_with_stats,
)


def test_empty_collection_report():
    result = process_document_collection_with_stats([])

    assert result == {
        "documents": [],
        "stats": {
            "total": 0,
            "unique": 0,
            "duplicates": 0,
        },
    }


def test_counts_duplicates_after_normalization():
    documents = [
        {"title": " PYTHON ", "content": "Learn Python"},
        {"title": "python", "content": " Learn Python "},
        {"title": "RAG", "content": "Retrieval"},
    ]

    result = process_document_collection_with_stats(documents)

    assert result["stats"] == {
        "total": 3,
        "unique": 2,
        "duplicates": 1,
    }


def test_keeps_same_title_with_different_content():
    documents = [
        {"title": "Python", "content": "Basic"},
        {"title": "PYTHON", "content": "Advanced"},
    ]

    result = process_document_collection_with_stats(documents)

    assert result["stats"]["unique"] == 2
    assert result["stats"]["duplicates"] == 0


def test_content_case_remains_significant():
    documents = [
        {"title": "Python", "content": "Hello"},
        {"title": "python", "content": "hello"},
    ]

    result = process_document_collection_with_stats(documents)

    assert result["stats"]["unique"] == 2


def test_preserves_first_occurrence_order():
    documents = [
        {"title": "Java", "content": "JVM"},
        {"title": "Python", "content": "Language"},
        {"title": "JAVA", "content": "JVM"},
        {"title": "RAG", "content": "Retrieval"},
    ]

    result = process_document_collection_with_stats(documents)

    titles = [
        document["title"]
        for document in result["documents"]
    ]

    assert titles == ["java", "python", "rag"]


def test_does_not_modify_input():
    documents = [
        {"title": " Python ", "content": " Example "}
    ]

    original = deepcopy(documents)

    result = process_document_collection_with_stats(documents)

    assert documents == original

    result["documents"][0]["title"] = "changed"

    assert documents == original


@pytest.mark.parametrize(
    "invalid_documents",
    [
        None,
        "invalid",
        {"title": "Python", "content": "Example"},
    ],
)
def test_rejects_invalid_collection_type(invalid_documents):
    with pytest.raises(TypeError):
        process_document_collection_with_stats(invalid_documents)


def test_rejects_invalid_document_type():
    documents = [
        {"title": "Python", "content": "Example"},
        123,
    ]

    with pytest.raises(TypeError):
        process_document_collection_with_stats(documents)


def test_legacy_api_is_unchanged():
    documents = [
        {"title": "Python", "content": "Basic"},
        {"title": "PYTHON", "content": "Basic"},
    ]

    old_result = process_document_collection(documents)
    new_result = process_document_collection_with_stats(documents)

    assert isinstance(old_result, list)
    assert old_result == new_result["documents"]


def test_statistics_invariant():
    documents = [
        {"title": "A", "content": "One"},
        {"title": "A", "content": "One"},
        {"title": "B", "content": "Two"},
        {"title": "B", "content": "Two"},
        {"title": "C", "content": "Three"},
    ]

    result = process_document_collection_with_stats(documents)

    stats = result["stats"]

    assert stats["total"] == stats["unique"] + stats["duplicates"]
    assert stats["total"] == 5
    assert stats["unique"] == 3
    assert stats["duplicates"] == 2