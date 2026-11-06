from document_collection_processor import (
    process_document_collection_with_stats,
)


class DocumentBatchError(Exception):
    """Error relacionado con la validación de un lote."""


def validate_document_batch(
    documents,
    /,
    *,
    reject_duplicates=False,
):
    if type(reject_duplicates) is not bool:
        raise TypeError("reject_duplicates debe ser bool")

    try:
        report = process_document_collection_with_stats(documents)
    except (TypeError, ValueError, KeyError) as error:
        raise DocumentBatchError(
            "Invalid document collection"
        ) from error

    if reject_duplicates and report["stats"]["duplicates"] > 0:
        raise DocumentBatchError(
            "Duplicate documents are not allowed"
        )

    return report