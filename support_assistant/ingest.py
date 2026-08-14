
from pathlib import Path

import chromadb

from .config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    DOCS_DIR
)

from .embeddings import embed_documents


def load_documents() -> tuple[list[str], list[str], list[dict]]:
    """
    Load all corpus documents.

    Since the provided documents are short, we use one
    document = one chunk.

    Returns:
        ids
        documents
        metadatas
    """

    files = sorted(
        DOCS_DIR.glob("doc_*.txt")
    )

    if len(files) != 8:
        raise RuntimeError(
            f"Expected exactly 8 documents, "
            f"but found {len(files)} in {DOCS_DIR}"
        )

    ids = []
    documents = []
    metadatas = []

    for file_path in files:

        text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            raise ValueError(
                f"Document is empty: {file_path}"
            )

        doc_id = file_path.stem

        # One document = one chunk.
        chunk_id = f"{doc_id}_chunk_01"

        ids.append(chunk_id)
        documents.append(text)

        metadatas.append(
            {
                "doc_id": doc_id,
                "source_file": file_path.name,
                "chunk_id": chunk_id
            }
        )

    return ids, documents, metadatas


def create_chroma_collection():
    """
    Create a persistent local ChromaDB collection.
    """

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # Delete old collection so ingestion is deterministic.
    try:
        client.delete_collection(
            name=COLLECTION_NAME
        )

        print(
            f"Deleted existing collection: "
            f"{COLLECTION_NAME}"
        )

    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": (
                "Zepto support policy corpus "
                "for Module 3"
            )
        }
    )

    return collection


def ingest():
    """
    Complete ingestion pipeline.
    """

    print("=" * 60)
    print("ZEpto Support Assistant - Ingestion")
    print("=" * 60)

    ids, documents, metadatas = load_documents()

    print(
        f"Loaded {len(documents)} documents."
    )

    collection = create_chroma_collection()

    print("Creating embeddings...")

    embeddings = embed_documents(
        documents
    )

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(
        f"Inserted {len(ids)} chunks into ChromaDB."
    )

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    print(
        f"Database path: {CHROMA_DIR}"
    )

    print("=" * 60)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    ingest()
