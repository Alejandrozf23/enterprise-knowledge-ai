from copy import deepcopy

from document_normalizer import normalize_documents


def process_document_collection(documents):
    normalized_documents = normalize_documents(documents)

    seen = set()
    result = []

    for document in normalized_documents:
        key = (document["title"], document["content"])

        if key not in seen:
            seen.add(key)
            result.append(deepcopy(document))

    return result