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