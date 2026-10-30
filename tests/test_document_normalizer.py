import pytest

from document_normalizer import normalize_document
from document_normalizer import normalize_documents
from document_normalizer import normalize_title
from document_normalizer import group_titles_by_source
from document_normalizer import unique_document_titles
from document_normalizer import rank_documents

@pytest.mark.parametrize(
    "title,content,expected_title,expected_content,expected_count",
    [
        (" ", " ", "", "", 0),
        (" Document ", "Hello  world", "document", "Hello  world", 2),
        (" Python and GenAI ", " Python allows to build agents ", "python and genai", "Python allows to build agents", 5),
        ("  TITLE  ", "\nHello\tWORLD\n", "title", "Hello\tWORLD", 2),
        ("Document", "", "document", "", 0)
    ]
)
def test_normal_document(title, content, expected_title, expected_content, expected_count):
    result = normalize_document(title, content)

    assert result["title"] == expected_title
    assert result["content"] == expected_content
    assert result["word_count"] == expected_count

def test_normal_document_rejects_none_content():
    with pytest.raises(TypeError, match="title and content"):
        normalize_document("Document", None)

@pytest.mark.parametrize("title", [None, 123, [], {}])
def test_normal_document_rejects_invalid_title(title):
    with pytest.raises(TypeError, match="title and content"):
        normalize_document(title, "Content ok")

def test_normalize_multiple_documents():
    documents = [{ "title":"Python ", "content":" Learn Python "}, { "title":"  GenAI  ", "content":"  LLM and RAG  "}]
    result = normalize_documents(documents)
    assert result == [
        {
            "title": "python",
            "content": "Learn Python",
            "word_count": 2
        },
        {
            "title": "genai",
            "content": "LLM and RAG",
            "word_count": 3
        }
    ]

def test_normalize_documents_does_not_mutate_input():
    documents = [{"title": "  Python  ", "content": "  Aprende Python  "}    ]

    result = normalize_documents(documents)

    assert documents == [
        {
            "title": "  Python  ",
            "content": "  Aprende Python  "
        }
    ]

    assert result[0]["title"] == "python"

    assert result is not documents
    assert result[0] is not documents[0]

def test_normalize_empty_documents():
    assert normalize_documents([]) == []

@pytest.mark.parametrize("invalid_documents",[None, 123, "documents", {}])
def test_normalize_documents_rejects_invalid_content(invalid_documents):
    with pytest.raises(TypeError):
        normalize_documents(invalid_documents)

@pytest.mark.parametrize("invalid_document",[None, 123, "document", []])
def test_normalize_documents_rejects_invalid_item(invalid_document):
    with pytest.raises(TypeError):
        normalize_documents([invalid_document])

def test_normalize_title_multiple_documents():
    documents = [{ "title":"Python ", "content":" Learn Python "}, { "title":"  GenAI  ", "content":"  LLM and RAG  "}]
    result = normalize_title(documents)
    assert result == ["python","genai"]

def test_group_titles_by_source():
    documents = [{"title":"Python", "metadata":{"source":"GenAI"}}, {"title":"Spark", "metadata":{"source":"GenAI"}}, {"title":"Java", "metadata":{"source":"APX"}}]
    result = group_titles_by_source(documents)
    assert len(result.get("GenAI")) == 2
    assert len(result.get("APX")) == 1

@pytest.mark.parametrize("invalid_documents", [None, 123, "documents", {}])
def test_unique_document_titles_rejects_invalid_content(invalid_documents):
    with pytest.raises(TypeError):
        unique_document_titles(invalid_documents)


@pytest.mark.parametrize("invalid_document", [None, 123, "document", []])
def test_unique_document_titles_rejects_invalid_item(invalid_document):
    with pytest.raises(TypeError):
        unique_document_titles([invalid_document])


def test_unique_document_titles_multiple_documents():
    documents = [
        {"title": "  Python  "},
        {"title": "python"},
        {"title": "GenAI "},
        {"title": "  GENAI"}
    ]
    result = unique_document_titles(documents)
    assert result == ["python", "genai"]


def test_unique_document_titles_empty_list():
    result = unique_document_titles([])
    assert result == []


def test_unique_document_titles_missing_key():
    documents = [{"name": "Missing Title Key"}]
    with pytest.raises(KeyError):
        unique_document_titles(documents)

@pytest.mark.parametrize("invalid_documents", [None, 123, "documents", {}])
def test_rank_documents_rejects_invalid_content(invalid_documents):
    with pytest.raises(TypeError):
        rank_documents(invalid_documents, [0.95])

@pytest.mark.parametrize("out_of_bounds_score", [-0.1, 1.1, 2.0, 123])
def test_rank_documents_rejects_out_of_bounds_score(out_of_bounds_score):
    with pytest.raises(ValueError):
        rank_documents(["doc_1"], [out_of_bounds_score])

def test_rank_documents_multiple_documents():
    document_ids = ["doc_1", "doc_2", "doc_3"]
    scores = [0.95, 0.85, 0.91]

    # Filtrado por defecto (min_score=0.90)
    result = rank_documents(document_ids, scores)
    assert result == [
        {"rank": 1, "document_id": "doc_1", "score": 0.95},
        {"rank": 3, "document_id": "doc_3", "score": 0.91}
    ]


def test_rank_documents_custom_min_score():
    document_ids = ["doc_1", "doc_2"]
    scores = [0.85, 0.70]

    result = rank_documents(document_ids, scores, min_score=0.70)
    assert result == [
        {"rank": 1, "document_id": "doc_1", "score": 0.85},
        {"rank": 2, "document_id": "doc_2", "score": 0.70}
    ]


def test_rank_documents_mismatched_lengths():
    # Al usar strict=True, si las listas difieren en tamaño arrojará un ValueError
    with pytest.raises(ValueError):
        rank_documents(["doc_1", "doc_2"], [0.95])


def test_rank_documents_empty_lists():
    result = rank_documents([], [])
    assert result == []