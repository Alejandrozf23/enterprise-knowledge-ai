from copy import deepcopy

from document_normalizer import normalize_documents

def process_document_collection_with_stats(documents):
    normalized_documents = normalize_documents(documents)

    seen = set()
    result = []

    for document in normalized_documents:
        key = (document["title"], document["content"])

        if key in seen:
            continue

        seen.add(key)
        result.append(deepcopy(document))

    total = len(normalized_documents)
    unique = len(result)

    return {
        "documents": result,
        "stats": {
            "total": total,
            "unique": unique,
            "duplicates": total - unique,
        },
    }


def process_document_collection(documents):
    return process_document_collection_with_stats(documents)["documents"]