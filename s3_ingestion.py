from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote_plus

from document_ingestion import (
    load_document_batch,
    load_jsonl_batch,
)


MAX_OBJECT_BYTES = 5 * 1024 * 1024


def extract_s3_objects(event):
    if not isinstance(event, dict):
        raise TypeError("event must be a dictionary")

    records = event.get("Records")

    if not isinstance(records, list):
        raise TypeError("Records must be a list")

    result = []

    for record in records:
        if not isinstance(record, dict):
            raise TypeError("invalid record")

        s3 = record.get("s3")
        if not isinstance(s3, dict):
            raise TypeError("invalid s3")

        bucket = s3.get("bucket")
        s3_object = s3.get("object")

        if not isinstance(bucket, dict):
            raise TypeError("invalid bucket")

        if not isinstance(s3_object, dict):
            raise TypeError("invalid object")

        bucket_name = bucket.get("name")
        key = s3_object.get("key")

        if not isinstance(bucket_name, str):
            raise TypeError("bucket.name must be a str")

        if not isinstance(key, str):
            raise TypeError("object.key must be a str")

        if not bucket_name or not key:
            raise ValueError("bucket and key cannot be empty")

        decoded_key = unquote_plus(key)

        if (
            decoded_key.startswith("incoming/")
            and decoded_key.endswith((".json", ".jsonl"))
        ):
            result.append({
                "bucket": bucket_name,
                "key": decoded_key,
            })

    return result


def load_s3_batch(
    s3_client,
    bucket,
    key,
    /,
    *,
    reject_duplicates=False,
):
    if not isinstance(bucket, str) or not isinstance(key, str):
        raise TypeError("bucket and key must be strings")

    if not bucket or not key:
        raise ValueError("bucket and key cannot be empty")

    if type(reject_duplicates) is not bool:
        raise TypeError("reject_duplicates must be bool")

    if key.endswith(".jsonl"):
        filename = "batch.jsonl"
        loader = load_jsonl_batch
    elif key.endswith(".json"):
        filename = "batch.json"
        loader = load_document_batch
    else:
        raise ValueError("unsupported extension")

    response = s3_client.get_object(
        Bucket=bucket,
        Key=key,
    )

    with closing(response["Body"]) as body:
        content = body.read(MAX_OBJECT_BYTES + 1)

    if len(content) > MAX_OBJECT_BYTES:
        raise ValueError("S3 object too large")

    with TemporaryDirectory() as folder:
        path = Path(folder) / filename
        path.write_bytes(content)

        return loader(
            path,
            reject_duplicates=reject_duplicates,
        )


def process_s3_event(
    event,
    s3_client,
    /,
    *,
    reject_duplicates=False,
):
    if type(reject_duplicates) is not bool:
        raise TypeError("reject_duplicates must be bool")

    objects = extract_s3_objects(event)
    results = []

    for item in objects:
        report = load_s3_batch(
            s3_client,
            item["bucket"],
            item["key"],
            reject_duplicates=reject_duplicates,
        )

        results.append({
            "bucket": item["bucket"],
            "key": item["key"],
            "stats": report["stats"],
        })

    return {
        "processed_objects": len(results),
        "results": results,
    }