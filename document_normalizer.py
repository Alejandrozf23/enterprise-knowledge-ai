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