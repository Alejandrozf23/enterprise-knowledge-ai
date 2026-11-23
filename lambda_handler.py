import logging
import json

from s3_ingestion import process_s3_event


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    if isinstance(event, dict) and event.get("Event") == "s3:TestEvent":
        return {
            "processed_objects": 0,
            "results": [],
        }

    import boto3

    s3_client = boto3.client("s3")

    report = process_s3_event(
        event,
        s3_client,
    )

    logger.info(
        "Successfully processed %s S3 objects",
        report["processed_objects"],
    )

    stats = {
        "total": 0,
        "unique": 0,
        "duplicates": 0,
    }

    for result in report["results"]:
        for key in stats:
            stats[key] += result["stats"][key]

    logger.info(
        "ingestion_summary %s",
        json.dumps(
            {
                "event": "ingestion_completed",
                "processed_objects": report["processed_objects"],
                "documents": stats,
            },
            sort_keys=True,
        ),
    )

    return report