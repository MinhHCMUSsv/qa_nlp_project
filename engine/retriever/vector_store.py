"""
Qdrant Vector Store Operations for TechQA

Manages collection lifecycle, indexing, and vector similarity search.
Supports both remote Qdrant service (Docker / cloud) and local in-memory/disk store.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union
from qdrant_client import QdrantClient
from qdrant_client.http import models
from engine.config import QdrantConfig, default_config

logger = logging.getLogger("techqa.vector_store")

Union_ID = Union[int, str]


class QdrantVectorStore:
    """Manager for Qdrant vector database operations."""

    def __init__(
        self,
        config: Optional[QdrantConfig] = None,
        client: Optional[QdrantClient] = None,
        in_memory: bool = False,
    ):
        self.config = config or default_config.qdrant
        self.collection_name = self.config.collection_name
        self.vector_size = self.config.vector_size

        if client is not None:
            self.client = client
        elif in_memory:
            self.client = QdrantClient(":memory:")
        elif self.config.url:
            try:
                self.client = QdrantClient(
                    url=self.config.url,
                    api_key=self.config.api_key,
                    timeout=float(os.getenv("QDRANT_TIMEOUT", "60.0")),
                )

                self.client.get_collections()
                logger.info(f"Connected to Qdrant Cloud at {self.config.url}")
            except Exception as e:
                logger.warning(f"Could not connect to Qdrant Cloud ({e}). Using in-memory Qdrant client fallback.")
                self.client = QdrantClient(":memory:")
        else:
            try:
                self.client = QdrantClient(host=self.config.host, port=self.config.port, timeout=3.0)
                # Check connection
                self.client.get_collections()
                logger.info(f"Connected to Qdrant at {self.config.host}:{self.config.port}")
            except Exception as e:
                logger.warning(f"Could not connect to Qdrant service ({e}). Using in-memory Qdrant client fallback.")
                self.client = QdrantClient(":memory:")


    def create_collection(
        self,
        collection_name: Optional[str] = None,
        vector_size: Optional[int] = None,
        distance: models.Distance = models.Distance.COSINE,
    ) -> bool:
        """Create a collection if it does not already exist."""
        name = collection_name or self.collection_name
        dim = vector_size or self.vector_size

        existing = [c.name for c in self.client.get_collections().collections]
        if name in existing:
            logger.info(f"Collection '{name}' already exists.")
            return True

        self.client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(size=dim, distance=distance),
        )
        logger.info(f"Created collection '{name}' with vector size {dim}.")
        return True

    def upsert_documents(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[Union_ID]] = None,
        collection_name: Optional[str] = None,
    ) -> int:
        """
        Upsert document vectors and payloads into Qdrant.
        
        Returns:
            Number of points indexed.
        """
        name = collection_name or self.collection_name
        self.create_collection(name)

        if not vectors:
            return 0

        point_ids = ids if ids is not None else list(range(len(vectors)))

        points = [
            models.PointStruct(id=p_id, vector=vec, payload=payload)
            for p_id, vec, payload in zip(point_ids, vectors, payloads)
        ]

        self.client.upsert(collection_name=name, points=points)
        logger.info(f"Upserted {len(points)} points into '{name}'.")
        return len(points)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for top-k nearest document vectors.
        
        Returns:
            List of matching records with id, score, and payload.
        """
        name = collection_name or self.collection_name
        try:
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=name,
                    query=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold,
                )
                results = getattr(response, "points", response)
            elif hasattr(self.client, "search"):
                results = self.client.search(
                    collection_name=name,
                    query_vector=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold,
                )
            else:
                results = []
        except Exception as e:
            logger.error(f"Search failed in collection '{name}': {e}")
            return []

        formatted = []
        for r in results:
            payload = r.payload or {}
            metadata = payload.get("metadata", {})
            
            # Extract content (support both flat and LangChain structure)
            content = payload.get("content") or payload.get("text") or payload.get("page_content") or ""
            
            # Extract title
            title = payload.get("title") or metadata.get("title") or "IBM Technote"
            
            # Extract doc_id
            doc_id = payload.get("doc_id") or metadata.get("id") or metadata.get("source_id") or str(r.id)

            formatted.append({
                "id": r.id,
                "score": round(float(r.score), 4),
                "payload": payload,
                "title": title,
                "content": content,
                "doc_id": doc_id,
                "url": payload.get("url") or metadata.get("url"),
            })
        return formatted


    def get_collection_info(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get collection statistics."""
        name = collection_name or self.collection_name
        try:
            info = self.client.get_collection(collection_name=name)
            return {
                "collection_name": name,
                "points_count": getattr(info, "points_count", 0) or 0,
                "indexed_vectors_count": getattr(info, "indexed_vectors_count", 0) or 0,
                "status": getattr(info, "status", "ready"),
            }
        except Exception:
            return {
                "collection_name": name,
                "points_count": 0,
                "indexed_vectors_count": 0,
                "status": "unavailable",
            }


Union_ID = int | str
