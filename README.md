# Multi-RAG AI Assistant

> Enterprise-grade Retrieval-Augmented Generation assistant with RBAC, guardrails, and document ingestion.

## Problem

Organizations need AI assistants that can answer questions from their private documents, but face critical challenges:

- **Data leakage** — A junior employee shouldn't access executive documents
- **Prompt attacks** — Injection, jailbreak, and PII leakage through LLM interactions
- **No traceability** — Black-box answers with no source attribution
- **Scattered knowledge** — Documents live across PDFs, spreadsheets, Word files, and text
- **No oversight** — No monitoring, cost tracking, or evaluation infrastructure

## Solution

A full-stack RAG platform with:

- **Role-based retrieval** — Qdrant metadata filters enforce department + sensitivity access at search time, not just UI hiding
- **Multi-layer guardrails** — Input (injection, jailbreak, PII, scope) + Output (PII redaction) safety
- **Source citations** — Every answer includes the exact document, chunk, and similarity score
- **Multi-format ingestion** — PDF, DOCX, CSV, XLSX — parse, chunk, embed, and store
- **Monitoring & evaluation** — Request metrics, cost tracking, and Ragas-based evaluation pipelines

## Features

- **Chat** — Conversational Q&A over ingested documents with streaming support
- **Documents** — Upload, tag (department + sensitivity), and manage knowledge sources
- **Monitoring** — Request volume, latency, token usage, cost, error rates, guardrail triggers
- **Evaluations** — Run Ragas evaluation jobs (faithfulness, answer relevancy, context precision/recall)
- **Admin** — User management, role assignment
- **Auth** — JWT-based registration/login with access + refresh tokens
- **Dark mode** — Full theme support

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, Tailwind CSS v4, Zustand, TanStack Query |
| Backend | FastAPI, LangGraph, LangChain-NVIDIA |
| Database | MongoDB (Beanie ODM) |
| Vector Store | Qdrant (metadata-filtered retrieval) |
| LLM | NVIDIA NIM (`meta/llama-3.1-70b-instruct`) |
| Embeddings | NVIDIA NIM (`nv-embedqa-e5-v5`, 1024-d) |
| Auth | JWT (access + refresh tokens) |
| Guardrails | Prompt injection, jailbreak, PII (Presidio), scope enforcement |

## File Structure

```
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── api/v1/              # REST routes (auth, chat, documents, etc.)
│   │   ├── core/                # Security, RBAC, exceptions
│   │   ├── db/                  # MongoDB + Qdrant connections
│   │   ├── guardrails/          # Injection, jailbreak, PII, scope
│   │   ├── ingestion/           # Parsers, chunker, pipeline
│   │   ├── middleware/          # Logging, monitoring middleware
│   │   ├── models/              # Beanie ODM models
│   │   ├── rag/                 # LangGraph pipeline, nodes, state
│   │   ├── schemas/             # Pydantic request/response models
│   │   └── services/            # Chat service, evaluation service
│   ├── scripts/                 # Seed users/documents
│   └── requirements.txt
├── frontend/                    # Next.js 16 frontend
│   ├── src/
│   │   ├── app/                 # Pages (chat, documents, admin, etc.)
│   │   ├── components/          # Landing page components
│   │   ├── lib/                 # API client, utilities
│   │   ├── stores/              # Zustand stores (auth, chat)
│   │   └── types/               # TypeScript interfaces
│   └── package.json
├── docs/                        # Additional documentation
├── data/                        # Evaluation datasets
├── docker-compose.yml           # Full-stack deployment
├── netlify.toml                 # Frontend deployment
└── render.yaml                  # Backend deployment
```

## Quick Start

### Prerequisites

- Docker Desktop (recommended) OR Python 3.9+ / Node.js 18+
- NVIDIA NIM API key ([get one here](https://build.nvidia.com/))

### 1. Clone & Configure

```bash
git clone https://github.com/krrish2803/Multi-RAG-AI-Assistant.git
cd "Multi-RAG-AI-Assistant"
cp .env.example .env
```

Edit `.env` and set at minimum:

```ini
NVIDIA_API_KEY=nvapi-your-key-here
JWT_SECRET_KEY=your-random-64-char-string
```

### 2. Run with Docker (easiest)

```bash
docker compose up --build

# Seed demo users
docker compose exec backend python scripts/seed_users.py
```

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **MongoDB:** localhost:27017
- **Qdrant Dashboard:** http://localhost:6333

### 3. Or Run Without Docker

**Backend:**

```bash
cd backend
python3 -m pip install -r requirements.txt

# Ensure MongoDB 7+ is running locally
# Ensure Qdrant is running (or use Qdrant Cloud via QDRANT_URL)

export MONGO_URI="mongodb://localhost:27017/ragchatbot"
python3 scripts/seed_users.py
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**

```bash
cd frontend
npm install

# Set API URL
export NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

npm run build
npm start
```

## Test Credentials

After running `seed_users.py`, you can log in with any of these:

| Email | Password | Role | Access |
|-------|----------|------|--------|
| `admin@company.com` | `admin123` | Admin | Full access |
| `alice@company.com` | `employee123` | Employee | Company-wide docs |
| `hr@company.com` | `hr123` | HR | Company-wide + HR |
| `finance@company.com` | `finance123` | Finance | Company-wide + Finance |
| `marketing@company.com` | `marketing123` | Marketing | Company-wide + Marketing |
| `engineer@company.com` | `engineer123` | Engineering | Company-wide + Engineering |
| `exec@company.com` | `exec123` | Executive | All departments + all sensitivity levels |

## Usage

1. **Log in** — Use test credentials or register a new account
2. **Upload documents** — Go to Documents → Choose File → Select department + sensitivity → Upload
3. **Chat** — Go to Chat → Ask questions. Answers include source citations
4. **Query specific documents** — From the Documents page, click the chat icon on any ready document to scope your chat to that file
5. **Monitor** — Track request volume, latency, costs, and guardrail triggers
6. **Evaluate** — Run evaluation jobs to measure answer quality

## RBAC Model

Access is enforced at the **vector search level**:

| Role | Departments | Sensitivity |
|------|------------|-------------|
| Employee | company-wide | public, internal |
| HR | company-wide, hr | public, internal, confidential |
| Finance | company-wide, finance | public, internal, confidential |
| Marketing | company-wide, marketing | public, internal |
| Engineering | company-wide, engineering | public, internal, confidential |
| Executive | all departments | all levels |
| Admin | all departments | all levels |

## API Overview

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/health` | GET | No | Health check |
| `/api/v1/auth/register` | POST | No | Register user |
| `/api/v1/auth/login` | POST | No | Login, get tokens |
| `/api/v1/auth/refresh` | POST | Refresh | Refresh access token |
| `/api/v1/auth/me` | GET | Bearer | Current user info |
| `/api/v1/chat/send` | POST | Bearer | Send message (optional `document_ids` to scope) |
| `/api/v1/chat/send/stream` | POST | Bearer | Stream response via SSE |
| `/api/v1/chat/conversations` | GET | Bearer | List conversations |
| `/api/v1/documents/upload` | POST | Bearer | Upload file (PDF/DOCX/CSV/XLSX, max 100MB) |
| `/api/v1/documents` | GET | Bearer | List documents |
| `/api/v1/documents/{id}` | DELETE | Bearer | Delete document + embeddings |
| `/api/v1/monitoring/summary` | GET | Bearer | Dashboard metrics |
| `/api/v1/evaluation/run` | POST | Bearer | Start evaluation |

## License

MIT License — see [LICENSE](LICENSE).

Copyright (c) 2026
