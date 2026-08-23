"""
Tests for RAG pipeline orchestrator.
"""

from unittest.mock import MagicMock
import pytest
from engine.pipeline import RAGPipeline


@pytest.fixture
def mock_pipeline():
    """Build a mock RAG pipeline to test end-to-end orchestration logic."""
    mock_embedder = MagicMock()
    mock_embedder.encode_query.return_value = [0.1] * 1024

    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = [
        {
            "doc_id": "TECHNOTE-001",
            "title": "Fix WebSphere OOM",
            "content": "Increase -Xmx to 4096MB.",
            "score": 0.95,
        }
    ]

    mock_generator = MagicMock()
    mock_generator.generate.return_value = "To fix WebSphere OOM, increase -Xmx to 4096MB."

    pipeline = RAGPipeline(
        embedder=mock_embedder,
        vector_store=mock_vector_store,
        generator=mock_generator,
    )
    return pipeline


def test_pipeline_answer_with_rag(mock_pipeline):
    """Test full RAG answer flow."""
    question = "How to fix OutOfMemory in WebSphere?"
    result = mock_pipeline.answer(question=question, top_k=1, use_rag=True)

    assert result["question"] == question
    assert "4096MB" in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["doc_id"] == "TECHNOTE-001"
    assert result["context_used"] is True
    assert result["mode"] == "rag"
    assert result["latency_ms"] >= 0


def test_pipeline_answer_without_rag(mock_pipeline):
    """Test standalone direct LLM generation without context."""
    question = "General knowledge question"
    result = mock_pipeline.answer(question=question, use_rag=False)

    assert result["question"] == question
    assert len(result["sources"]) == 0
    assert result["context_used"] is False
    assert result["mode"] == "direct_llm"
