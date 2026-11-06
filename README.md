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