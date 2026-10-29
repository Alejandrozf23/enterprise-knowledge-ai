import pytest

from document_normalizer import normalize_document
from document_normalizer import normalize_documents
from document_normalizer import normalize_title
from document_normalizer import group_titles_by_source

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