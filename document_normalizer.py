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

def normalize_title(documents):
    if not isinstance(documents, list):
        raise TypeError("documents must be a list")

    normalized_titles = []

    for document in documents:
        if not isinstance(document, dict):
            raise TypeError("document must be a dict")
        normalized_titles.append(document["title"].strip().lower())

    return normalized_titles

def group_titles_by_source(documents):
    titles_by_source = {}

    for document in documents:
        source = document["metadata"]["source"]

        if source not in titles_by_source:
            titles_by_source[source] = []

        titles_by_source[source].append(document["title"])

    return titles_by_source

def unique_document_titles(documents):
    if not isinstance(documents, list):
        raise TypeError("documents must be a list")

    seen = set()
    result = []

    for document in documents:
        if not isinstance(document, dict):
            raise TypeError("document must be a dict")

        title = document["title"].strip().lower()

        if title not in seen:
            seen.add(title)
            result.append(title)

    return result

def rank_documents(document_ids, scores, min_score=0.90):
    if not isinstance(document_ids, list) or not isinstance(scores, list):
        raise TypeError("documents and scores must be a lists")

    result = []

    for rank, (document_id, score) in enumerate(
        zip(document_ids, scores, strict=True), start=1
    ):
        if not isinstance(document_id, str):
            raise TypeError("id must be a str")

        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise TypeError("score must be an int o float")

        if not 0 <= score <= 1:
            raise ValueError("score must be between 0 and 1")

        if score >= min_score:
            result.append({
                "rank": rank,
                "document_id": document_id,
                "score": score,
            })

    return result