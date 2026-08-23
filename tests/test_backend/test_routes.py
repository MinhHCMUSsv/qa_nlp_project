"""
Unit and Integration Tests for FastAPI Backend.

Covers:
- Root and health check endpoints
- Collection stats and indexing endpoints
- RAG question-answering with various retrieval modes and parameters
- Request validation and error handling
- Sample questions and evaluation metrics endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root status check."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "TechQA" in data["service"]


def test_health_endpoint():
    """Test /api/health returns valid system diagnostic."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "qdrant_connected" in data
    assert "model_loaded" in data
    assert "indexed_documents_count" in data
    assert data["indexed_documents_count"] > 0


def test_collections_endpoint():
    """Test /api/collections returns vector collection metadata."""
    response = client.get("/api/collections")
    assert response.status_code == 200
    data = response.json()
    assert data["collection_name"] == "techqa_documents"
    assert data["vector_size"] == 1024
    assert data["points_count"] >= 1


def test_index_endpoint():
    """Test /api/index triggers document indexing."""
    payload = {"corpus_split": "techqa_sample", "force_reindex": True}
    response = client.post("/api/index", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["indexed_count"] > 0
    assert "duration_seconds" in data


def test_sample_questions_endpoint():
    """Test /api/sample-questions returns curated question list."""
    response = client.get("/api/sample-questions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    for q in data:
        assert "id" in q
        assert "category" in q
        assert "question" in q
        assert "description" in q


def test_metrics_endpoint():
    """Test /api/metrics returns evaluation benchmarks for report."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "dataset" in data
    assert len(data["metrics"]) == 4
    for m in data["metrics"]:

        assert "method" in m
        assert m["rouge_l"] > 0
        assert m["bleu_4"] > 0
        assert m["f1_score"] > 0
    assert "conclusion" in data


def test_ask_endpoint_dense_retrieval():
    """Test /api/ask with standard RAG dense retrieval mode."""
    payload = {
        "question": "How to resolve WebSphere OutOfMemoryError in Java heap space?",
        "top_k": 3,
        "temperature": 0.7,
        "retrieval_mode": "dense",
    }
    response = client.post("/api/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == payload["question"]
    assert len(data["answer"]) > 50
    assert len(data["sources"]) == 3
    assert data["sources"][0]["score"] > 0
    assert (
        "OutOfMemoryError" in data["sources"][0]["title"]
        or "WebSphere" in data["sources"][0]["title"]
        or "IBM Technote" in data["sources"][0]["title"]
        or "WebSphere" in data["sources"][0]["content"]
    )
    assert data["latency_ms"] >= 0

    assert data["confidence_score"] > 0


def test_ask_endpoint_direct_llm_mode():
    """Test /api/ask with direct_llm mode (no retrieved documents)."""
    payload = {
        "question": "What is segmentation fault?",
        "top_k": 3,
        "temperature": 0.5,
        "retrieval_mode": "direct_llm",
    }
    response = client.post("/api/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["sources"]) == 0
    assert "Direct LLM" in data["answer"]


def test_ask_endpoint_validation_error():
    """Test /api/ask with invalid question (too short)."""
    payload = {"question": "a", "top_k": 5}
    response = client.post("/api/ask", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_ask_endpoint_top_k_bounds():
    """Test /api/ask with invalid top_k."""
    payload = {"question": "How to tune Linux kernel file descriptors?", "top_k": 50}
    response = client.post("/api/ask", json=payload)
    assert response.status_code == 422
