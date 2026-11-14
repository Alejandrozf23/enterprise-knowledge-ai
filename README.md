# enterprise-knowledge-ai
Sistema de gestión del conocimiento empresarial e Inteligencia Artificial corporativa, diseñado para alimentar agentes y sistemas RAG con la documentación interna de la compañía.

## Document Collection Processor

The document collection processor normalizes a list of documents
and removes duplicates while preserving their original order.

Features:
- Reuses the existing document normalizer.
- Deduplicates by normalized title and content.
- Preserves the first occurrence of each document.
- Avoids modifying the original input.
- Includes automated tests with pytest.

## Document batch validation

The batch validator provides an optional duplicate-rejection
policy for normalized document collections.

```python
from document_batch_validator import validate_document_batch

report = validate_document_batch(
    documents,
    reject_duplicates=True,
)
```

## Document ingestion

The project supports document ingestion from JSON arrays
and JSON Lines (JSONL) files.

- load_document_batch(): loads a JSON array.
- iter_jsonl_objects(): yields JSONL objects incrementally.
- load_jsonl_batch(): loads JSONL into the existing
  batch validation and deduplication pipeline.

JSONL parsing supports an optional skip_invalid flag.
Skipped malformed lines are excluded from batch statistics.

The batch loaders materialize document collections before
global deduplication; end-to-end streaming is not implemented yet.