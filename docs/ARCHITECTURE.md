# Architecture

## System Overview

The Enterprise Knowledge Assistant is a full-stack RAG application with secure role-based access control, built on a modular architecture.

```mermaid
graph TB
    FE[Next.js Frontend] -->|REST/SSE| BE[FastAPI Backend]
    BE -->|ODM| MDB[(MongoDB)]
    BE -->|Vector Search| QD[(Qdrant)]
    BE -->|LLM API| NIM[NVIDIA NIM]
    
    subgraph Backend Modules
        AUTH[Auth + RBAC]
        GR[Guardrails]
        RAG[RAG Pipeline]
        ING[Ingestion]
        MON[Monitoring]
    end
    
    BE --> AUTH
    BE --> GR
    BE --> RAG
    BE --> ING
    BE --> MON
```

## Request Lifecycle (Chat)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend API
    participant GR as Guardrails
    participant QD as Qdrant
    participant LLM as NVIDIA NIM
    participant DB as MongoDB

    U->>FE: Send message
    FE->>BE: POST /chat/send (JWT)
    BE->>BE: Validate JWT, extract role
    BE->>GR: Run input guards
    GR-->>BE: Injection/jailbreak/PII/scope check
    
    alt Blocked
        BE-->>FE: Refusal response
    else Safe
        BE->>QD: Search with RBAC filter
        QD-->>BE: Top-5 document chunks
        BE->>LLM: Generate with context
        LLM-->>BE: Response with citations
        BE->>GR: Run output guards
        GR-->>BE: PII redaction if needed
        BE->>DB: Save message + metrics
        BE-->>FE: Response + sources
    end
```

## Document Ingestion Flow

```mermaid
sequenceDiagram
    participant U as Admin User
    participant FE as Frontend
    participant BE as Upload API
    participant ING as Ingestion Pipeline
    participant QD as Qdrant
    participant DB as MongoDB

    U->>FE: Upload document + metadata
    FE->>BE: POST /documents/upload
    BE->>DB: Create document record (status: processing)
    BE-->>FE: Return document (processing)
    BE->>ING: Background: parse → chunk → embed → store
    ING->>ING: Parse file (PDF/DOCX/TXT/CSV)
    ING->>ING: Chunk text (512 chars, 64 overlap)
    ING->>ING: Embed chunks (NVIDIA NIM)
    ING->>QD: Upsert vectors with RBAC metadata
    ING->>DB: Update status to "ready"
```

## RBAC Enforcement Points

```mermaid
graph LR
    A[API Route] -->|Layer 1| B{Role Check}
    B -->|Allowed| C[Build Qdrant Filter]
    C -->|Layer 2| D{Metadata Filter}
    D -->|Dept + Sensitivity| E[Vector Search]
    E --> F[LLM Generation]
    F -->|Layer 3| G{Output Validation}
    G -->|Clean| H[Response to User]
    G -->|PII Found| I[Redact + Response]
```

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MongoDB over PostgreSQL | Beanie ODM | User-specified, flexible schema for documents |
| Qdrant over Pinecone/Weaviate | Self-hosted, metadata filtering | RBAC at retrieval time via payload filters |
| NVIDIA NIM | Configurable LLM provider | Enterprise-grade, OpenAI-compatible API |
| JWT over sessions | Stateless auth | Scales horizontally, works with microservices |
| Background asyncio tasks | Simple async | Can upgrade to Celery/Redis later |

## Scaling Considerations

- **Horizontal**: Backend is stateless, can scale behind load balancer
- **Caching**: Add Redis for conversation history and frequent queries
- **Queue**: Replace asyncio.create_task with Celery for reliable ingestion
- **CDN**: Frontend can be deployed to Vercel/Cloudflare
- **Vector DB**: Qdrant supports distributed mode for larger datasets
