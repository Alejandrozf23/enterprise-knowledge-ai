from document_collection_processor import process_document_collection_with_stats

def build_title_index(documents):
    processed_documents = process_document_collection(documents)
    title_index = {}

    for document in processed_documents:
        title = document["title"]

        if title not in title_index:
            title_index[title] = []

        title_index[title].append(document["content"])

    return title_index

def create_batch_report(
    documents,
    /,
    *,
    name="default",
    include_documents=False,
    **metadata
):
    if not isinstance(name, str):
        raise TypeError("name debe ser str")

    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("name no debe estar vacío")

    if type(include_documents) is not bool:
        raise TypeError("include_documents debe ser bool")

    processed = process_document_collection_with_stats(documents)

    report = {
        "name": normalized_name,
        "stats": processed["stats"],
        "metadata": metadata,
    }

    if include_documents:
        report["documents"] = processed["documents"]

    return report

class DocumentBatchError(Exception):
        pass


    def validate_document_batch(
        documents,
        /,
        *,
        reject_duplicates=False
    ):
        if type(reject_duplicates) is not bool:
            raise TypeError("reject_duplicates debe ser bool")

        try:
            report = process_document_collection_with_stats(documents)
        except (TypeError, ValueError, KeyError) as error:
            raise DocumentBatchError("Invalid document collection") from error

        if reject_duplicates and report["stats"]["duplicates"] > 0:
            raise DocumentBatchError("Duplicate documents are not allowed")

        return report