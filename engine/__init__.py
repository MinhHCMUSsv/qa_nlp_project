"""
QA Engine — Core AI logic for the Question Answering system.

This package contains the RAG pipeline components:
- embeddings: bge-m3 embedding model wrapper
- retriever: Qdrant vector store operations & document indexing
- generator: Fine-tuned Llama LLM wrapper
- pipeline: RAG pipeline orchestrator (retrieve → augment → generate)
- data: Dataset loading and preprocessing utilities
"""
