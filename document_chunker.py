from document_models import NormalizedDocument


def chunk_document(
    document,
    /,
    *,
    chunk_size=100,
    overlap=20,
):
    if not isinstance(document, NormalizedDocument):
        raise TypeError("document debe ser una instancia de NormalizedDocument")

    if type(chunk_size) is not int:
        raise TypeError("chunk_size debe ser int, no bool")

    if chunk_size <= 0:
        raise ValueError("chunk_size debe ser mayor que cero")

    if type(overlap) is not int:
        raise TypeError("overlap debe ser int, no bool")

    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap debe cumplir 0 <= overlap < chunk_size")

    words = document.content.split()
    result = []
    start = 0

    while start < len(words):
        chunk_words = words[start:start + chunk_size]

        result.append({
            "title": document.title,
            "chunk_index": len(result),
            "content": " ".join(chunk_words),
            "word_count": len(chunk_words),
        })

        if start + chunk_size >= len(words):
            break

        start += chunk_size - overlap

    return result