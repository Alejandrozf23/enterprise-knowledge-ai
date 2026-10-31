def normalize_document(title, content):
    if not isinstance(title, str) or not isinstance(content, str):
        raise TypeError("title and content must be String")

    normalized_title = title.strip().lower()
    normalized_content = content.strip()

    return {
        "title": normalized_title,
        "content": normalized_content,
        "word_count": len(normalized_content.split())
    }

def normalize_documents(documents):
    if not isinstance(documents, list):
        raise TypeError("documents must be a list")

    normalized_documents = []

    for document in documents:
        if not isinstance(document, dict):
            raise TypeError("document must be a dict")
        normalized_documents.append(normalize_document(document["title"], document["content"]))

    return normalized_documents
