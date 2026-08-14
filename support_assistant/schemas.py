
from typing import List

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """
    Request schema for POST /ask
    """

    query: str = Field(
        ...,
        min_length=1,
        description="User's support question"
    )


class AskResponse(BaseModel):
    """
    Validated response returned by the support assistant.
    """

    answer: str = Field(
        ...,
        min_length=1
    )

    sources: List[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )
