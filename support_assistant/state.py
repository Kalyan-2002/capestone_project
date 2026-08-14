
from typing import TypedDict, List, Optional


class SupportState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    # Original user query
    query: str

    # Intent classification
    intent: str

    # Routing decision
    route: str

    # Retrieved context
    retrieved_context: str

    # IDs of retrieved chunks
    sources: List[str]

    # Final generated answer
    answer: str

    # Confidence score
    confidence: float

    # Optional error information
    error: Optional[str]
