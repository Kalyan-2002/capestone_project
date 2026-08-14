
import os
from pathlib import Path


BASE_DIR = Path('/content/Support-Assistant/support_assistant')

DOCS_DIR = BASE_DIR / "docs"

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_support"


EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


MOCK_LLM = os.getenv("MOCK_LLM", "1") == "1"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.1-8b-instant"
)


# Retrieval configuration

TOP_K = 1

SNIPPET_LENGTH = 200



# Mock confidence

MOCK_CONFIDENCE = 1.0
