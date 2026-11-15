from document_models import NormalizedDocument


def build_chunks(
    document,
    /,
    *,
    strategy="fixed",
    chunk_size=100,
    overlap=20,
):
    if not isinstance(document, NormalizedDocument):
        raise TypeError("document debe ser una instancia de NormalizedDocument")

    if type(strategy) is not str:
        raise TypeError("strategy debe ser str")

    normalized_strategy = strategy.strip().lower()

    match normalized_strategy:
        case "fixed":
            return chunk_document(
                document,
                chunk_size=chunk_size,
                overlap=overlap,
            )
        case "single":
            return chunk_document(
                document,
                chunk_size=max(1, len(document.content.split())),
                overlap=0,
            )
        case _:
            raise ValueError(f"Estrategia desconocida: {normalized_strategy}")