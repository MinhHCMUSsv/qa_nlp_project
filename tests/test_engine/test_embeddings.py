"""
Tests for bge-m3 embedding module.
"""

from unittest.mock import MagicMock, patch
import numpy as np
import pytest
from engine.config import EmbeddingConfig
from engine.embeddings.bge_m3 import BGEM3Embedder


@pytest.fixture
def mock_embedder():
    """Mock embedder returning deterministic 1024-d vectors."""
    config = EmbeddingConfig(model_name="mock-bge-m3", device="cpu")
    embedder = BGEM3Embedder(config=config)
    
    # Mock the internal model to avoid downloading 2.2GB model during unit test suite
    mock_model = MagicMock()
    mock_model.encode.side_effect = lambda texts, **kwargs: np.ones((len(texts), 1024), dtype=np.float32)
    embedder._model = mock_model
    return embedder


def test_embed_single_query(mock_embedder):
    """Test embedding a single query text."""
    query = "How to resolve WebSphere crash?"
    vec = mock_embedder.encode_query(query)
    assert len(vec) == 1024
    assert isinstance(vec[0], float)


def test_embed_batch_texts(mock_embedder):
    """Test embedding a batch of documents."""
    docs = [
        "Technote 1: DB2 lock timeout resolution.",
        "Technote 2: IBM MQ queue depth management.",
    ]
    vectors = mock_embedder.encode(docs)
    assert len(vectors) == 2
    assert len(vectors[0]) == 1024
    assert len(vectors[1]) == 1024


def test_embed_empty_list(mock_embedder):
    """Test embedding empty list returns empty list."""
    assert mock_embedder.encode([]) == []
