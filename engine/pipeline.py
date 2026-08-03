"""
RAG Pipeline Orchestrator

Combines retriever and generator into a single QA pipeline:
1. Encode user question via bge-m3
2. Retrieve top-k relevant documents from Qdrant
3. Construct augmented prompt (question + context)
4. Generate answer via fine-tuned Llama

Usage:
    from engine.pipeline import RAGPipeline

    pipeline = RAGPipeline()
    result = pipeline.answer("How to fix segmentation fault in C++?")
    print(result.answer)
    print(result.sources)  # Retrieved documents used
"""

# TODO: Implement in Phase 3
# - RAGPipeline class combining embedder + retriever + generator
# - answer() method returning answer + source documents
# - Prompt template management
# - Configurable retrieval parameters
