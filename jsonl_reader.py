from pathlib import Path
import json


def iter_jsonl_objects(path, /, *, skip_invalid=False):
    if not isinstance(path, (str, Path)):
        raise TypeError("path debe ser str o pathlib.Path")

    if type(skip_invalid) is not bool:
        raise TypeError("skip_invalid debe ser bool")

    def generate_objects():
        with open(path, "r", encoding="utf-8") as file:
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