from document_models import NormalizedDocument


def chunk_document(
    document,
    /,
    *,
    chunk_size=100,
    overlap=20,
):
    if not isinstance(document, NormalizedDocument):
        raise TypeError(
            "document must be an instance of NormalizedDocument"
        )

    if type(chunk_size) is not int:
        raise TypeError("chunk_size should be int, not bool")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if type(overlap) is not int:
        raise TypeError("overlap should be int, not bool")

    if not 0 <= overlap < chunk_size:
        raise ValueError(
            "overlap must meet 0 <= overlap < chunk_size"
        )

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


def build_chunks(
    document,
    /,
    *,
    strategy="fixed",
    chunk_size=100,
    overlap=20,
):
    if not isinstance(document, NormalizedDocument):
        raise TypeError(
            "document must be an instance of NormalizedDocument"
        )

    if type(strategy) is not str:
        raise TypeError("strategy must be str")

    normalized_strategy = strategy.strip().lower()

    match normalized_strategy:
        case "fixed":
            return chunk_document(
                document,
                chunk_size=chunk_size,
                overlap=overlap,
            )

        case "single":
            return chunk_document(
                document,
                chunk_size=max(1, len(document.content.split())),
                overlap=0,
            )

        case _:
            raise ValueError(
                f"Unknown strategy: {normalized_strategy}"
            )