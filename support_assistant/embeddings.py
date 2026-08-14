
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from .config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.

    The model runs locally.
    No LLM API is used here.
    """

    print(
        f"Loading embedding model: {EMBEDDING_MODEL_NAME}"
    )

    model = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    return model


def embed_text(text: str) -> list[float]:
    """
    Convert text into an embedding vector.
    """

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


def embed_documents(
    documents: list[str]
) -> list[list[float]]:
    """
    Convert multiple documents into embedding vectors.
    """

    model = get_embedding_model()

    embeddings = model.encode(
        documents,
        normalize_embeddings=True
    )

    return embeddings.tolist()
