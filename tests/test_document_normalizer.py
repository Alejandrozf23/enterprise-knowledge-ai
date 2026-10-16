import pytest
from document_normalizer import normalize_document

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