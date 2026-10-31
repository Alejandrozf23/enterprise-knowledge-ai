from copy import deepcopy

import pytest

from document_collection_processor import process_document_collection


def test_empty_collection():
    assert process_document_collection([]) == []


def test_normalizes_documents():
    documents = [
        {
            "title": " PYTHON ",
            "content": " Introducción a Python "
        }
    ]

    result = process_document_collection(documents)

    assert len(result) == 1
    assert result[0]["title"] == "python"
    assert result[0]["content"] == "Introducción a Python"


def test_removes_duplicates_after_normalization():
    documents = [
        {"title": " PYTHON ", "content": "Learn Python"},
        {"title": "python", "content": " Learn Python "},
    ]

    result = process_document_collection(documents)

    assert len(result) == 1
    assert result[0]["title"] == "python"


def test_keeps_same_title_with_different_content():
    documents = [
        {"title": "Python", "content": "Basic course"},
        {"title": "Python", "content": "Advanced course"},
    ]

    result = process_document_collection(documents)

    assert len(result) == 2


def test_keeps_different_titles_with_same_content():
    documents = [
        {"title": "Python", "content": "Introduction"},
        {"title": "Java", "content": "Introduction"},
    ]

    result = process_document_collection(documents)

    assert len(result) == 2


def test_preserves_first_occurrence_order():
    documents = [
        {"title": "Java", "content": "JVM"},
        {"title": "Python", "content": "Language"},
        {"title": "JAVA", "content": "JVM"},
        {"title": "RAG", "content": "Retrieval"},
    ]

    result = process_document_collection(documents)

    assert [doc["title"] for doc in result] == [
        "java",
        "python",
        "rag",
    ]


def test_does_not_modify_input():
    documents = [
        {"title": " Python ", "content": " Example "}
    ]

    original = deepcopy(documents)

    result = process_document_collection(documents)

    assert documents == original

    result[0]["title"] = "modified"

    assert documents == original


@pytest.mark.parametrize(
    "invalid_documents",
    [
        None,
        "not a list",
        {"title": "Python", "content": "Example"},
    ],
)
def test_rejects_invalid_collection_type(invalid_documents):
    with pytest.raises(TypeError):
        process_document_collection(invalid_documents)


def test_rejects_invalid_document():
    documents = [
        {"title": "Python", "content": "Example"},
        "invalid document",
    ]

    with pytest.raises(TypeError):
        process_document_collection(documents)