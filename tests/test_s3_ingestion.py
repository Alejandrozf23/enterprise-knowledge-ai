import json
import sys
from io import BytesIO
from types import SimpleNamespace

import pytest

import s3_ingestion
from lambda_handler import lambda_handler
from document_batch_validator import DocumentBatchError
from s3_ingestion import (
    extract_s3_objects,
    load_s3_batch,
    process_s3_event,
)


class FakeS3:
    def __init__(self, objects):
        self.objects = objects
        self.calls = []
        self.bodies = []

    def get_object(self, *, Bucket, Key):
        self.calls.append((Bucket, Key))

        body = BytesIO(self.objects[Key])
        self.bodies.append(body)

        return {"Body": body}


def make_event(*keys):
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "test-input"},
                    "object": {"key": key},
                }
            }
            for key in keys
        ]
    }


def test_extract_decodes_and_filters():
    result = extract_s3_objects(
        make_event(
            "incoming/rag+notes.jsonl",
            "processed/output.json",
            "incoming/guide.json",
        )
    )

    assert result == [
        {
            "bucket": "test-input",
            "key": "incoming/rag notes.jsonl",
        },
        {
            "bucket": "test-input",
            "key": "incoming/guide.json",
        },
    ]


def test_extract_empty_event():
    assert extract_s3_objects(make_event()) == []


@pytest.mark.parametrize(
    "event",
    [
        None,
        {},
        {"Records": "invalid"},
        {"Records": [{"s3": {}}]},
    ],
)
def test_extract_rejects_invalid_events(event):
    with pytest.raises(TypeError):
        extract_s3_objects(event)


@pytest.mark.parametrize(
    "bucket,key,error_type",
    [
        ("", "incoming/a.json", ValueError),
        ("test-input", None, TypeError),
    ],
)
def test_extract_validates_bucket_and_key(
    bucket,
    key,
    error_type,
):
    event = make_event("incoming/a.json")

    event["Records"][0]["s3"]["bucket"]["name"] = bucket
    event["Records"][0]["s3"]["object"]["key"] = key

    with pytest.raises(error_type):
        extract_s3_objects(event)


def test_load_json_from_fake_s3():
    client = FakeS3({
        "incoming/batch.json": (
            b'[{"title":" RAG ","content":"one two"}]'
        )
    })

    report = load_s3_batch(
        client,
        "test-input",
        "incoming/batch.json",
    )

    assert report["stats"] == {
        "total": 1,
        "unique": 1,
        "duplicates": 0,
    }

    assert client.calls == [
        ("test-input", "incoming/batch.json")
    ]

    assert client.bodies[0].closed


def test_load_jsonl_from_fake_s3():
    client = FakeS3({
        "incoming/batch.jsonl": (
            b'{"title":" RAG ","content":"one"}\n'
            b'{"title":"rag","content":"one"}\n'
        )
    })

    report = load_s3_batch(
        client,
        "test-input",
        "incoming/batch.jsonl",
    )

    assert report["stats"]["duplicates"] == 1
    assert client.bodies[0].closed


def test_duplicate_policy_is_preserved():
    client = FakeS3({
        "incoming/batch.json": (
            b'[{"title":"RAG","content":"one"},'
            b'{"title":" rag ","content":"one"}]'
        )
    })

    with pytest.raises(DocumentBatchError):
        load_s3_batch(
            client,
            "test-input",
            "incoming/batch.json",
            reject_duplicates=True,
        )


def test_body_closes_after_invalid_json():
    client = FakeS3({
        "incoming/broken.json": b"{broken"
    })

    with pytest.raises(json.JSONDecodeError):
        load_s3_batch(
            client,
            "test-input",
            "incoming/broken.json",
        )

    assert client.bodies[0].closed


def test_object_size_limit(monkeypatch):
    monkeypatch.setattr(
        s3_ingestion,
        "MAX_OBJECT_BYTES",
        4,
    )

    client = FakeS3({
        "incoming/batch.json": b"12345"
    })

    with pytest.raises(ValueError, match="too large"):
        load_s3_batch(
            client,
            "test-input",
            "incoming/batch.json",
        )

    assert client.bodies[0].closed


def test_invalid_extension_does_not_call_s3():
    client = FakeS3({})

    with pytest.raises(ValueError):
        load_s3_batch(
            client,
            "test-input",
            "incoming/file.txt",
        )

    assert client.calls == []


def test_process_event_filters_and_preserves_order():
    client = FakeS3({
        "incoming/first.json": (
            b'[{"title":"A","content":"one"}]'
        ),
        "incoming/second.jsonl": (
            b'{"title":"B","content":"two"}\n'
        ),
    })

    event = make_event(
        "incoming/first.json",
        "processed/output.json",
        "incoming/second.jsonl",
    )

    result = process_s3_event(event, client)

    assert result["processed_objects"] == 2
    assert [item["key"] for item in result["results"]] == [
        "incoming/first.json",
        "incoming/second.jsonl",
    ]

    assert len(client.calls) == 2


def test_process_empty_event():
    assert process_s3_event(
        make_event(),
        FakeS3({}),
    ) == {
        "processed_objects": 0,
        "results": [],
    }


def test_process_propagates_errors():
    client = FakeS3({
        "incoming/broken.json": b"{invalid"
    })

    with pytest.raises(json.JSONDecodeError):
        process_s3_event(
            make_event("incoming/broken.json"),
            client,
        )


def test_reject_duplicates_flag_is_immediate():
    with pytest.raises(TypeError):
        process_s3_event(
            make_event(),
            FakeS3({}),
            reject_duplicates=1,
        )


def test_lambda_handler_uses_s3_client(monkeypatch):
    client = FakeS3({
        "incoming/batch.json": (
            b'[{"title":"RAG","content":"one"}]'
        )
    })

    fake_boto3 = SimpleNamespace(
        client=lambda service: client
    )

    monkeypatch.setitem(
        sys.modules,
        "boto3",
        fake_boto3,
    )

    result = lambda_handler(
        make_event("incoming/batch.json"),
        None,
    )

    assert result["processed_objects"] == 1
    assert len(client.calls) == 1


def test_lambda_handler_accepts_s3_test_event():
    result = lambda_handler(
        {"Event": "s3:TestEvent"},
        None,
    )

    assert result == {
        "processed_objects": 0,
        "results": [],
    }