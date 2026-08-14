
import chromadb

from .config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    TOP_K
)

from .embeddings import embed_text


def get_chroma_collection():
    """
    Connect to the persistent ChromaDB collection.
    """

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME
        )
    except Exception as exc:
        raise RuntimeError(
            "ChromaDB collection does not exist. "
            "Run ingestion first:\n\n"
            "python -m support_assistant.ingest"
        ) from exc

    return collection


def retrieve(
    query: str,
    top_k: int = TOP_K
) -> tuple[str, list[str]]:
    """
    Retrieve the most similar chunk from ChromaDB.

    Returns:
        retrieved_context
        sources
    """

    collection = get_chroma_collection()

    query_embedding = embed_text(
        query
    )

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = result.get(
        "documents",
        [[]]
    )[0]

    ids = result.get(
        "ids",
        [[]]
    )[0]

    if not documents:
        return "", []

    retrieved_context = "\n\n".join(
        documents
    )

    return retrieved_context, ids
