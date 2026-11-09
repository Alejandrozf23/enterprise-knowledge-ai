from DocumentRecord import DocumentRecord

class ReviewedDocumentRecord(DocumentRecord):
    def __init__(self, title, content, tags=None, *, reviewer="pending"):
        super().__init__(title, content, tags)

        if not isinstance(reviewer, str):
            raise TypeError("reviewer debe ser un string")

        normalized_reviewer = reviewer.strip()
        if not normalized_reviewer:
            raise ValueError("reviewer no debe estar vacío")

        self.reviewer = normalized_reviewer

    def to_dict(self):
        result = super().to_dict()
        result["reviewer"] = self.reviewer
        return result