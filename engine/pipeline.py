"""
RAG Pipeline Orchestrator for TechQA

Combines:
1. BGEM3Embedder: Query & Document embedding (1024-dim dense vectors)
2. QdrantVectorStore: Vector similarity search & metadata retrieval
3. LlamaGenerator: Context-augmented generation using Llama 3.2 (AQUABOT/Llama-3.2-3B-TechQA)
"""

import logging
import time
from typing import Any, Dict, List, Optional
from engine.config import EngineConfig, default_config
from engine.embeddings.bge_m3 import BGEM3Embedder
from engine.retriever.vector_store import QdrantVectorStore
from engine.generator.llm import LlamaGenerator

logger = logging.getLogger("techqa.pipeline")


class RAGPipeline:
    """End-to-End Retrieval-Augmented Generation Pipeline."""

    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        embedder: Optional[BGEM3Embedder] = None,
        vector_store: Optional[QdrantVectorStore] = None,
        generator: Optional[LlamaGenerator] = None,
    ):
        self.config = config or default_config
        self.embedder = embedder or BGEM3Embedder(self.config.embedding)
        self.vector_store = vector_store or QdrantVectorStore(self.config.qdrant)
        self.generator = generator or LlamaGenerator(self.config.llm)
        logger.info("RAGPipeline initialized successfully.")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant technote documents for a query."""
        k = top_k or self.config.rag.top_k
        query_vector = self.embedder.encode_query(query)
        if not query_vector:
            return []
        return self.vector_store.search(query_vector=query_vector, top_k=k)

    def answer(
        self,
        question: str,
        top_k: Optional[int] = None,
        use_rag: bool = True,
        temperature: Optional[float] = None,
        max_new_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute full RAG workflow to answer a user question.
        
        Args:
            question: Technical query string.
            top_k: Number of reference documents to retrieve.
            use_rag: If False, performs direct LLM generation without context.
            temperature: Sampling temperature.
            max_new_tokens: Maximum tokens to generate.
            
        Returns:
            Dictionary with generated answer, retrieved sources, and execution metrics.
        """
        start_time = time.time()
        sources = []
        context = ""

        if use_rag:
            sources = self.retrieve(question, top_k=top_k)
            if sources:
                context_blocks = []
                for i, doc in enumerate(sources):
                    title = doc.get("title", "IBM Technote")
                    doc_id = doc.get("doc_id", f"DOC-{i+1}")
                    content = doc.get("content", "").strip()
                    context_blocks.append(f"[{doc_id}] {title}:\n{content}")
                context = "\n\n".join(context_blocks)

        answer_text = self.generator.generate(
            prompt=question,
            context=context if use_rag else None,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "question": question,
            "answer": answer_text,
            "sources": sources,
            "context_used": bool(context),
            "mode": "rag" if use_rag else "direct_llm",
            "latency_ms": latency_ms,
        }
