"""
API Routes

Endpoints:
- POST /api/ask        — Ask a question, get RAG-powered answer
- GET  /api/health     — Health check with system status
- POST /api/index      — Trigger document indexing
- GET  /api/collections — Get Qdrant collection stats
"""

from fastapi import APIRouter, HTTPException
from backend.api.schemas import QuestionRequest, AnswerResponse, HealthResponse

router = APIRouter()


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and receive a RAG-powered answer.

    The pipeline:
    1. Embeds the question via bge-m3
    2. Retrieves top-k relevant documents from Qdrant
    3. Generates an answer using fine-tuned Llama 3.2
    """
    # TODO: Implement in Phase 4
    # - Call QAService.answer(request.question)
    # - Return answer + source documents
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health: API, Qdrant, and model status."""
    # TODO: Implement in Phase 4
    return HealthResponse(
        status="ok",
        qdrant_connected=False,
        model_loaded=False,
    )


@router.post("/index")
async def index_documents():
    """Trigger indexing of TechQA corpus into Qdrant."""
    # TODO: Implement in Phase 4
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/collections")
async def get_collections():
    """Get Qdrant collection statistics."""
    # TODO: Implement in Phase 4
    raise HTTPException(status_code=501, detail="Not implemented yet")
