"""
API Routes for TechQA system.

Endpoints:
- POST /api/ask              — Ask a question, get RAG-powered answer + sources + latency
- GET  /api/health           — Health check with system status (API, Qdrant, Model)
- GET  /api/collections      — Get Qdrant collection statistics
- POST /api/index            — Trigger document indexing
- GET  /api/sample-questions — Get curated TechQA benchmark questions
- GET  /api/metrics          — Get model evaluation & statistical metrics for report
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status

from backend.api.schemas import (
    AnswerResponse,
    CollectionStats,
    EvaluationMetricsResponse,
    HealthResponse,
    IndexRequest,
    IndexResponse,
    QuestionRequest,
    SampleQuestion,
)
from backend.services.qa_service import qa_service

logger = logging.getLogger("techqa.api.routes")
router = APIRouter()


@router.post(
    "/ask",
    response_model=AnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a technical question",
    description="Processes user query via RAG: embeds query, retrieves top-k documents, and generates grounded answer.",
)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and receive a RAG-powered answer.

    The pipeline:
    1. Embeds the question (via bge-m3 / vector scoring)
    2. Retrieves top-k relevant documents from TechQA corpus / Qdrant
    3. Synthesizes an accurate technical solution grounded in verified technotes
    """
    try:
        response = qa_service.answer(
            question=request.question,
            top_k=request.top_k,
            temperature=request.temperature,
            retrieval_mode=request.retrieval_mode,
            session_id=request.session_id,
        )
        return response
    except Exception as e:
        logger.error(f"Error processing question '{request.question}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}",
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health & Diagnostic",
    description="Returns availability status for API server, Vector DB, and LLM model.",
)
async def health_check():
    """Check system health: API, Qdrant, and model status."""
    try:
        return qa_service.get_health()
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check error: {str(e)}",
        )


@router.get(
    "/collections",
    response_model=CollectionStats,
    status_code=status.HTTP_200_OK,
    summary="Vector Collection Statistics",
    description="Returns information on indexed points, vector dimensions, and status.",
)
async def get_collections():
    """Get Qdrant collection statistics."""
    try:
        return qa_service.get_collection_stats()
    except Exception as e:
        logger.error(f"Error fetching collection stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch collection stats: {str(e)}",
        )


@router.post(
    "/index",
    response_model=IndexResponse,
    status_code=status.HTTP_200_OK,
    summary="Index Document Corpus",
    description="Triggers embedding and indexing of technical documents into vector database.",
)
async def index_documents(request: IndexRequest = IndexRequest()):
    """Trigger indexing of TechQA corpus into Qdrant."""
    try:
        return qa_service.index_documents(
            corpus_split=request.corpus_split,
            force_reindex=request.force_reindex,
        )
    except Exception as e:
        logger.error(f"Error during indexing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(e)}",
        )


@router.get(
    "/sample-questions",
    response_model=List[SampleQuestion],
    status_code=status.HTTP_200_OK,
    summary="Sample Benchmark Questions",
    description="Returns curated TechQA technical questions by category for quick testing.",
)
async def get_sample_questions():
    """Get sample TechQA questions."""
    try:
        return qa_service.get_sample_questions()
    except Exception as e:
        logger.error(f"Error fetching sample questions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sample questions: {str(e)}",
        )


@router.get(
    "/metrics",
    response_model=EvaluationMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Model Evaluation & Statistical Metrics",
    description="Returns benchmark evaluation results comparing Base, Fine-tuned, and RAG architectures.",
)
async def get_evaluation_metrics():
    """Get model evaluation and statistical benchmark metrics for course project."""
    try:
        return qa_service.get_evaluation_metrics()
    except Exception as e:
        logger.error(f"Error fetching evaluation metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch metrics: {str(e)}",
        )
