"""
Tests for Qdrant retriever module using in-memory client.
"""

import pytest
from engine.config import QdrantConfig
from engine.retriever.vector_store import QdrantVectorStore


@pytest.fixture
def vector_store():
    """In-memory vector store for unit tests."""
    config = QdrantConfig(collection_name="test_collection", vector_size=4)
    store = QdrantVectorStore(config=config, in_memory=True)
    store.create_collection()
    return store


def test_create_collection(vector_store):
    """Test creating a collection in Qdrant."""
    info = vector_store.get_collection_info()
    assert info["collection_name"] == "test_collection"
    assert info["status"] != "unavailable"


def test_upsert_and_search_documents(vector_store):
    """Test indexing document vectors and searching with cosine similarity."""
    vectors = [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
    ]
    payloads = [
        {"title": "Doc 1: WebSphere OOM", "content": "Fixing OutOfMemoryError in WAS", "doc_id": "DOC-1"},
        {"title": "Doc 2: DB2 Deadlock", "content": "Resolving SQL0911N in DB2", "doc_id": "DOC-2"},
        {"title": "Doc 3: IBM MQ Full", "content": "Handling queue full 2053 in MQ", "doc_id": "DOC-3"},
    ]

    count = vector_store.upsert_documents(vectors=vectors, payloads=payloads)
    assert count == 3

    # Query closely aligned with Doc 1
    query_vec = [0.95, 0.05, 0.0, 0.0]
    results = vector_store.search(query_vec, top_k=2)

    assert len(results) == 2
    assert results[0]["doc_id"] == "DOC-1"
    assert results[0]["title"] == "Doc 1: WebSphere OOM"
    assert results[0]["score"] > 0.9


def test_search_empty_collection():
    """Test search on an empty collection returns empty list without error."""
    config = QdrantConfig(collection_name="empty_collection", vector_size=4)
    store = QdrantVectorStore(config=config, in_memory=True)
    store.create_collection()

    results = store.search([1.0, 0.0, 0.0, 0.0], top_k=5)
    assert results == []
