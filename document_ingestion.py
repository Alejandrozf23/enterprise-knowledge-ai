import json
from pathlib import Path

from document_batch_validator import validate_document_batch


def load_document_batch(
    path,
    /,
    *,
    reject_duplicates=False,
):
    if not isinstance(path, (str, Path)):
        raise TypeError("path debe ser str o pathlib.Path")

    if type(reject_duplicates) is not bool:
        raise TypeError("reject_duplicates debe ser bool")

    with Path(path).open("r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise TypeError("el JSON debe representar una lista")

    return validate_document_batch(
        documents,
        reject_duplicates=reject_duplicates,
    )


def iter_jsonl_objects(
    path,
    /,
    *,
    skip_invalid=False,
):
    if not isinstance(path, (str, Path)):
        raise TypeError("path debe ser str o pathlib.Path")

    if type(skip_invalid) is not bool:
        raise TypeError("skip_invalid debe ser bool")

    def generate_objects():
        with Path(path).open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    if skip_invalid:
                        continue

                    raise ValueError(
                        f"Invalid JSON on line {line_number}"
                    ) from error

                if not isinstance(record, dict):
                    if skip_invalid:
                        continue

                    raise TypeError(
                        f"Expected JSON object on line {line_number}"
                    )

                yield record

    return generate_objects()


def load_jsonl_batch(
    path,
    /,
    *,
    reject_duplicates=False,
    skip_invalid=False,
):
    if type(reject_duplicates) is not bool:
        raise TypeError("reject_duplicates debe ser bool")

    records = list(
        iter_jsonl_objects(
            path,
            skip_invalid=skip_invalid,
        )
    )

    return validate_document_batch(
        records,
        reject_duplicates=reject_duplicates,
    )