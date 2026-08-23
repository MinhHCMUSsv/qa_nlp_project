"""
Engine configuration — centralized settings for all AI components.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()



@dataclass
class EmbeddingConfig:
    """Configuration for the embedding model."""
    model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
    device: str = os.getenv("DEVICE", "cuda")
    max_length: int = 8192  # bge-m3 supports up to 8192 tokens
    batch_size: int = 32


@dataclass
class QdrantConfig:
    """Configuration for the Qdrant vector store."""
    host: str = os.getenv("QDRANT_HOST", "localhost")
    port: int = int(os.getenv("QDRANT_PORT", "6333"))
    url: Optional[str] = os.getenv("QDRANT_URL", None)
    api_key: Optional[str] = os.getenv("QDRANT_API_KEY", None)
    collection_name: str = os.getenv("QDRANT_COLLECTION_NAME", "techqa_corpus")
    vector_size: int = 1024  # bge-m3 dense vector dimension



@dataclass
class LLMConfig:
    """Configuration for the LLM generator."""
    model_path: str = os.getenv("LLM_MODEL_PATH", "models/Llama_TechQA")
    model_name: str = os.getenv(
        "LLM_MODEL_NAME", "unsloth/Llama-3.2-3B-Instruct-bnb-4bit"
    )
    device: str = os.getenv("DEVICE", "cuda")
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9


@dataclass
class RAGConfig:
    """Configuration for the RAG pipeline."""
    top_k: int = 5  # Number of documents to retrieve
    chunk_size: int = 512  # Token chunk size for document splitting
    chunk_overlap: int = 50  # Overlap between chunks


@dataclass
class EngineConfig:
    """Master configuration combining all sub-configs."""
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)


# Global config instance
config = EngineConfig()
default_config = config

