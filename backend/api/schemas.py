"""
Pydantic Schemas for API request/response validation.
"""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """Request body for the /ask endpoint."""
    question: str = Field(
        ...,
        description="The user's question in natural language",
        min_length=1,
        max_length=2000,
        examples=["How to resolve an out-of-memory error in Java?"],
    )
    top_k: int = Field(
        default=5,
        description="Number of documents to retrieve",
        ge=1,
        le=20,
    )


class SourceDocument(BaseModel):
    """A retrieved source document."""
    content: str = Field(description="Document text content")
    score: float = Field(description="Similarity score (0-1)")
    metadata: dict = Field(default_factory=dict, description="Document metadata")


class AnswerResponse(BaseModel):
    """Response body for the /ask endpoint."""
    answer: str = Field(description="Generated answer text")
    sources: list[SourceDocument] = Field(
        default_factory=list,
        description="Retrieved source documents used to generate the answer",
    )
    question: str = Field(description="Original question (echoed back)")


class HealthResponse(BaseModel):
    """Response body for the /health endpoint."""
    status: str = Field(description="API status")
    qdrant_connected: bool = Field(description="Whether Qdrant is reachable")
    model_loaded: bool = Field(description="Whether the LLM model is loaded")
