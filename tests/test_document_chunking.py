import pytest

from document_models import NormalizedDocument
from document_chunking import chunk_document, build_chunks


def make_document(content="one two three four five"):
    return NormalizedDocument(
        title="rag",
        content=content,
        word_count=len(content.split()),
    )


def test_fixed_overlap_and_metadata():
    result = chunk_document(
        make_document(),
        chunk_size=3,
        overlap=1,
    )

    assert result == [
        {
            "title": "rag",
            "chunk_index": 0,
            "content": "one two three",
            "word_count": 3,
        },
        {
            "title": "rag",
            "chunk_index": 1,
            "content": "three four five",
            "word_count": 3,
        },
    ]


def test_zero_overlap():
    result = chunk_document(
        make_document(),
        chunk_size=2,
        overlap=0,
    )

    assert [chunk["content"] for chunk in result] == [
        "one two",
        "three four",
        "five",
    ]


def test_empty_document():
    assert chunk_document(
        make_document(""),
        chunk_size=2,
        overlap=1,
    ) == []


def test_no_redundant_final_chunk():
    result = chunk_document(
        make_document(),
        chunk_size=4,
        overlap=3,
    )

    assert [chunk["content"] for chunk in result] == [
        "one two three four",
        "two three four five",
    ]


def test_does_not_modify_document():
    document = make_document()
    original = document.to_dict()

    chunks = chunk_document(
        document,
        chunk_size=3,
        overlap=1,
    )

    chunks[0]["content"] = "modified"

    assert document.to_dict() == original


def test_single_strategy():
    result = build_chunks(
        make_document(),
        strategy="single",
    )

    assert len(result) == 1
    assert result[0]["content"] == "one two three four five"
    assert result[0]["chunk_index"] == 0


def test_single_empty_document():
    assert build_chunks(
        make_document(""),
        strategy="single",
    ) == []


def test_single_ignores_chunk_options():
    result = build_chunks(
        make_document(),
        strategy="single",
        chunk_size=None,
        overlap=True,
    )

    assert len(result) == 1


def test_fixed_strategy_normalization():
    result = build_chunks(
        make_document(),
        strategy=" FIXED ",
        chunk_size=3,
        overlap=1,
    )

    assert [chunk["content"] for chunk in result] == [
        "one two three",
        "three four five",
    ]


def test_invalid_document():
    with pytest.raises(TypeError):
        chunk_document({"title": "rag"})

    with pytest.raises(TypeError):
        build_chunks({"title": "rag"})


@pytest.mark.parametrize(
    "chunk_size,error_type",
    [
        (0, ValueError),
        (-1, ValueError),
        (True, TypeError),
        ("3", TypeError),
    ],
)
def test_invalid_chunk_size(chunk_size, error_type):
    with pytest.raises(error_type):
        chunk_document(
            make_document(),
            chunk_size=chunk_size,
            overlap=0,
        )


@pytest.mark.parametrize(
    "overlap,error_type",
    [
        (-1, ValueError),
        (3, ValueError),
        (True, TypeError),
        ("1", TypeError),
    ],
)
def test_invalid_overlap(overlap, error_type):
    with pytest.raises(error_type):
        chunk_document(
            make_document(),
            chunk_size=3,
            overlap=overlap,
        )


@pytest.mark.parametrize(
    "strategy,error_type",
    [
        (None, TypeError),
        ("random", ValueError),
    ],
)
def test_invalid_strategy(strategy, error_type):
    with pytest.raises(error_type):
        build_chunks(
            make_document(),
            strategy=strategy,
        )