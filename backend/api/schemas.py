"""
Pydantic Schemas for API request/response validation.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """Request body for the /ask endpoint."""

    question: str = Field(
        ...,
        description="The user's technical question in natural language",
        min_length=3,
        max_length=2000,
        examples=["How to resolve WebSphere Application Server OutOfMemoryError in Java heap?"],
    )
    top_k: int = Field(
        default=5,
        description="Number of documents to retrieve",
        ge=1,
        le=20,
    )
    temperature: float = Field(
        default=0.7,
        description="LLM sampling temperature",
        ge=0.0,
        le=1.5,
    )
    retrieval_mode: str = Field(
        default="dense",
        description="Retrieval strategy: 'dense' (bge-m3), 'hybrid', or 'direct_llm' (no RAG)",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session or conversation ID",
    )


class SourceDocument(BaseModel):
    """A retrieved source document / technote used for RAG answer generation."""

    doc_id: str = Field(description="Unique identifier of the document / technote")
    title: str = Field(description="Document title or technote header")
    content: str = Field(description="Document text content or relevant snippet")
    score: float = Field(description="Similarity relevance score between 0.0 and 1.0")
    category: Optional[str] = Field(default="IBM Technote", description="Document category")
    url: Optional[str] = Field(default=None, description="External reference URL if available")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional document metadata (e.g. technote_id, chunk_index, token_count)",
    )


class AnswerResponse(BaseModel):
    """Response body for the /ask endpoint."""

    question: str = Field(description="Original question (echoed back)")
    answer: str = Field(description="Generated answer in markdown format")
    sources: List[SourceDocument] = Field(
        default_factory=list,
        description="Retrieved source documents used to ground the answer",
    )
    latency_ms: float = Field(
        default=0.0,
        description="Total response generation latency in milliseconds",
    )
    retrieval_mode: str = Field(
        default="dense",
        description="Retrieval mode used for this query",
    )
    model_name: str = Field(
        default="Llama-3.2-3B-Instruct (Fine-tuned TechQA)",
        description="LLM generator name",
    )
    confidence_score: float = Field(
        default=0.92,
        description="Confidence / grounding score of the answer based on retrieved context",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for tracking",
    )


class HealthResponse(BaseModel):
    """Response body for the /health endpoint."""

    status: str = Field(description="Overall API status ('healthy' or 'degraded')")
    qdrant_connected: bool = Field(description="Whether Qdrant vector DB is reachable")
    model_loaded: bool = Field(description="Whether LLM model is ready")
    embedder_loaded: bool = Field(description="Whether bge-m3 embedding model is ready")
    engine_mode: str = Field(
        description="Engine operating mode: 'engine_live' (GPU/Qdrant) or 'demo_corpus' (In-memory Knowledge Base)",
    )
    indexed_documents_count: int = Field(
        description="Total number of indexed documents in the active vector store / corpus",
    )
    device: str = Field(description="Compute device (e.g., cuda, cpu)")
    version: str = Field(default="0.1.0", description="TechQA service version")


class CollectionStats(BaseModel):
    """Qdrant collection statistics and metadata."""

    collection_name: str = Field(description="Name of the collection")
    points_count: int = Field(description="Number of indexed vector points / chunks")
    vector_size: int = Field(description="Dimension of the embedding vectors (e.g. 1024 for bge-m3)")
    distance_metric: str = Field(default="Cosine", description="Distance metric used for indexing")
    status: str = Field(description="Collection status ('green', 'yellow', 'ready')")


class IndexRequest(BaseModel):
    """Request to trigger indexing or re-indexing."""

    corpus_split: str = Field(
        default="techqa_all",
        description="Corpus subset to index ('techqa_sample', 'techqa_all')",
    )
    force_reindex: bool = Field(
        default=False,
        description="Whether to overwrite existing collection",
    )


class IndexResponse(BaseModel):
    """Response from document indexing."""

    status: str = Field(description="Indexing job status")
    indexed_count: int = Field(description="Number of documents successfully indexed")
    collection_name: str = Field(description="Target collection name")
    duration_seconds: float = Field(description="Time elapsed during indexing")


class SampleQuestion(BaseModel):
    """Sample technical support question for fast testing."""

    id: str = Field(description="Sample question ID")
    category: str = Field(description="Category (e.g., WebSphere, DB2, Java, MQ, Security)")
    question: str = Field(description="The technical question text")
    description: str = Field(description="Brief explanation of the scenario or issue")


class MetricItem(BaseModel):
    """Individual model evaluation metric item."""

    method: str = Field(description="Evaluation method or model name")
    rouge_1: float = Field(description="ROUGE-1 F1 score (0-100)")
    rouge_2: float = Field(description="ROUGE-2 F1 score (0-100)")
    rouge_l: float = Field(description="ROUGE-L F1 score (0-100)")
    bleu_4: float = Field(description="BLEU-4 score (0-100)")
    exact_match: float = Field(description="Exact Match % (0-100)")
    f1_score: float = Field(description="Token-level F1 score (0-100)")
    avg_latency_ms: float = Field(description="Average latency in ms per query")
    hallucination_rate: float = Field(description="Hallucination rate percentage (%)")


class EvaluationMetricsResponse(BaseModel):
    """Benchmark evaluation results comparing model configurations for course project report."""

    dataset: str = Field(default="PrimeQA/TechQA Benchmark", description="Evaluation dataset")
    test_samples_count: int = Field(default=800, description="Number of evaluated test samples")
    metrics: List[MetricItem] = Field(description="Comparative evaluation metrics table")
    conclusion: str = Field(description="Brief statistical conclusion summarizing RAG impact")
