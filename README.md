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