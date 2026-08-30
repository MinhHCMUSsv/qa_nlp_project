"""
bge-m3 Embedding Wrapper for TechQA

Wraps the BAAI/bge-m3 model for dense semantic embedding of queries and technotes.
Outputs 1024-dimensional normalized dense vectors.
"""

import logging
from typing import List, Optional, Union
import torch
from engine.config import EmbeddingConfig, default_config

logger = logging.getLogger("techqa.embedder")


class BGEM3Embedder:
    """Wrapper around BAAI/bge-m3 for dense vector representations."""

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or default_config.embedding
        self._model = None
        self._device = self._resolve_device()

    def _resolve_device(self) -> str:
        """Automatically resolve device to cuda if available."""
        if self.config.device == "cuda" and not torch.cuda.is_available():
            logger.info("CUDA not available for embedding, falling back to CPU.")
            return "cpu"
        return self.config.device if torch.cuda.is_available() else "cpu"

    @property
    def model(self):
        """Lazy load SentenceTransformer or HuggingFace model."""
        if self._model is None:
            logger.info(f"Loading embedding model '{self.config.model_name}' on {self._device}...")
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.config.model_name, device=self._device)
            except Exception as e:
                logger.warning(f"SentenceTransformer load failed: {e}. Trying transformers...")
                from transformers import AutoModel, AutoTokenizer
                self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
                self._hf_model = AutoModel.from_pretrained(self.config.model_name).to(self._device)
                self._hf_model.eval()
                self._model = "hf_fallback"
            logger.info("Embedding model loaded successfully.")
        return self._model

    def encode(self, texts: Union[str, List[str]], batch_size: Optional[int] = None) -> List[List[float]]:
        """
        Generate 1024-d dense embeddings for given texts.
        
        Args:
            texts: Single string or list of text strings.
            batch_size: Batch size for encoding.
            
        Returns:
            List of vector embeddings (lists of floats).
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        batch_size = batch_size or self.config.batch_size
        model = self.model

        if model != "hf_fallback":
            embeddings = model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            return embeddings.tolist()
        else:
            # Fallback manual mean pooling
            all_embeddings = []
            with torch.no_grad():
                for i in range(0, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    encoded = self._tokenizer(
                        batch,
                        padding=True,
                        truncation=True,
                        max_length=self.config.max_length,
                        return_tensors="pt"
                    ).to(self._device)
                    out = self._hf_model(**encoded)
                    # Use CLS token or mean pooling
                    cls_rep = out.last_hidden_state[:, 0]
                    norm_rep = torch.nn.functional.normalize(cls_rep, p=2, dim=1)
                    all_embeddings.extend(norm_rep.cpu().tolist())
            return all_embeddings

    def encode_query(self, query: str) -> List[float]:
        """Encode a single query string into a vector."""
        res = self.encode([query])
        return res[0] if res else []

    embed_query = encode_query
    embed_documents = encode

