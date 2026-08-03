"""
QA Service — Business logic bridging API and Engine.

This service layer decouples the FastAPI routes from the engine internals,
making it easy to swap out components or add caching, logging, etc.

Usage:
    from backend.services.qa_service import QAService

    service = QAService()
    result = service.answer("How to fix segfault?")
"""

# TODO: Implement in Phase 4
# - Initialize engine pipeline on startup
# - answer() method calling engine.pipeline
# - index_corpus() method
# - get_stats() method for Qdrant collection info
# - Error handling and logging
