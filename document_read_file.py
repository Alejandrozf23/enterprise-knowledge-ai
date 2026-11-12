from pathlib import Path
import json

from document_batch_validator import validate_document_batch


def load_document_batch(path, /, *, reject_duplicates=False):
    if not isinstance(path, (str, Path)):
        raise TypeError("path debe ser str o pathlib.Path")

    if type(reject_duplicates) is not bool:
        raise TypeError("reject_duplicates debe ser bool")

    with open(path, "r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise TypeError("el JSON debe representar una lista")

    return validate_document_batch(
        documents,
        reject_duplicates=reject_duplicates,
    )

def iter_document_titles(documents, /, *, min_words=0):
    if type(min_words) is not int:
        raise TypeError("min_words debe ser int, no bool")

    if min_words < 0:
        raise ValueError("min_words no debe ser negativo")

    def generate_titles():
        for document in process_document_collection(documents):
            if document["word_count"] >= min_words:
                yield document["title"]

    return generate_titles()