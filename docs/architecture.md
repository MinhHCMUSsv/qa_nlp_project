# Architecture Documentation

> Detailed architecture documentation will be added as the system is implemented.

## System Overview

The TechQA system follows a **3-layer architecture**:

1. **Engine** — Core AI logic (embedding, retrieval, generation)
2. **Backend** — FastAPI REST API server
3. **Frontend** — React (Vite) web interface

## Data Flow

```mermaid
flowchart TD
    subgraph Frontend["React Frontend (Vite — port 5173)"]
        UI["ChatWindow · Sidebar · Inspector"]
    end

    subgraph Backend["FastAPI Backend (Uvicorn — port 8000)"]
        API["/api/ask · /api/health · /api/index"]
    end

    subgraph Engine["QA Engine"]
        direction LR
        EMB["bge-m3 Embedder"] --> RET["Qdrant Retriever (top-k)"] --> GEN["Llama 3.2-3B Generator (fine-tuned)"]
    end

    subgraph Qdrant["Qdrant Server (Docker — port 6333)"]
        QDB["Storage · Dashboard · Metrics"]
    end

    Frontend -->|"HTTP (REST API)"| Backend
    Backend -->|"Python import"| Engine
    RET -->|"gRPC / HTTP"| Qdrant
```
