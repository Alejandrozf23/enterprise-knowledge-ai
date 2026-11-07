def make_batch_validator(*, reject_duplicates=False):
    if type(reject_duplicates) is not bool:
        raise TypeError("reject_duplicates debe ser bool")

    def validator(documents):
        return validate_document_batch(
            documents,
            reject_duplicates=reject_duplicates,
        )

    return validator