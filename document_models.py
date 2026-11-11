from dataclasses import dataclass

from document_batch_validator import validate_document_batch


@dataclass(frozen=True)
class NormalizedDocument:
    title: str
    content: str
    word_count: int

    def __post_init__(self):
        if type(self.title) is not str:
            raise TypeError("title must be str")

        if type(self.content) is not str:
            raise TypeError("content must be str")

        if type(self.word_count) is not int:
            raise TypeError("word_count must be int")

        if self.title != self.title.strip().lower():
            raise ValueError("title must be normalized")

        if self.content != self.content.strip():
            raise ValueError("content must be normalized")

        if self.word_count != len(self.content.split()):
            raise ValueError("word_count does not match with content")

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "word_count": self.word_count,
        }


def build_document_records(
    documents,
    /,
    *,
    reject_duplicates=False,
):
    report = validate_document_batch(
        documents,
        reject_duplicates=reject_duplicates,
    )

    records = [
        NormalizedDocument(
            title=document["title"],
            content=document["content"],
            word_count=document["word_count"],
        )
        for document in report["documents"]
    ]

    return {
        "documents": records,
        "stats": report["stats"],
    }