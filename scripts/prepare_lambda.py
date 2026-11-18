from pathlib import Path
from shutil import copy2, rmtree

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "build" / "lambda"

FILES = (
    "document_normalizer.py",
    "document_collection_processor.py",
    "document_batch_validator.py",
    "document_models.py",
    "document_ingestion.py",
    "document_chunking.py",
    "s3_ingestion.py",
    "lambda_handler.py",
    "requirements.txt",
)


def main():
    if TARGET.exists():
        rmtree(TARGET)

    TARGET.mkdir(parents=True)

    for filename in FILES:
        source = ROOT / filename

        if not source.is_file():
            raise FileNotFoundError(source)

        copy2(source, TARGET / filename)

    print(f"Prepared {len(FILES)} files in {TARGET}")


if __name__ == "__main__":
    main()