"""
FastAPI Application Entry Point

Run with:
    uvicorn backend.main:app --reload --port 8000
API documentation:
    http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.services.qa_service import qa_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("techqa.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    logger.info("Starting up TechQA API Server...")
    # Initialize service
    qa_service.initialize()
    yield
    logger.info("Shutting down TechQA API Server...")


app = FastAPI(
    title="TechQA API — Transformer-based QA System",
    description=(
        "Retrieval-Augmented Generation (RAG) Question Answering API for IBM Technical Support Questions. "
        "Built with FastAPI, bge-m3 embeddings, Qdrant vector database, and fine-tuned Llama 3.2-3B."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration — allow React frontend dev server and production origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes under /api prefix
app.include_router(router, prefix="/api")


@app.get("/", summary="Root Health Endpoint")
async def root():
    """Root status and API overview."""
    return {
        "status": "ok",
        "service": "TechQA API — Transformer-based QA System",
        "version": "0.1.0",
        "docs_url": "/docs",
        "api_prefix": "/api",
    }
