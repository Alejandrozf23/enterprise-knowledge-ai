import logging

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

    return report