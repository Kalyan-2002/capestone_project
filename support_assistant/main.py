
from fastapi import (
    FastAPI,
    HTTPException
)

from .config import MOCK_LLM

from .schemas import (
    AskRequest,
    AskResponse
)

from .graph import support_graph


app = FastAPI(
    title="Zepto Support Assistant",
    description=(
        "Module 3 GenAI Support Assistant using "
        "LangGraph, ChromaDB, Sentence Transformers "
        "and FastAPI."
    ),
    version="1.0.0"
)


@app.get("/")
def root():
    """
    Basic health endpoint.
    """

    return {
        "service": "Zepto Support Assistant",
        "status": "running",
        "mock_llm": MOCK_LLM
    }


@app.get("/health")
def health():
    """
    Health check.
    """

    return {
        "status": "ok",
        "mock_llm": MOCK_LLM
    }


@app.post(
    "/ask",
    response_model=AskResponse
)
def ask(
    request: AskRequest
):
    """
    Main support assistant endpoint.

    Input:
        {"query": "How much is delivery?"}

    Output:
        {
            "answer": "...",
            "sources": [...],
            "confidence": 1.0
        }
    """

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    try:

        result = support_graph.invoke(
            {
                "query": query
            }
        )

        response = AskResponse(
            answer=result["answer"],
            sources=result.get(
                "sources",
                []
            ),
            confidence=result.get(
                "confidence",
                1.0
            )
        )

        return response

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc
