# Enterprise Internal Knowledge Assistant

An open-source full-stack retrieval-augmented generation (RAG) assistant for enterprise knowledge workflows. It combines a secure FastAPI backend with a modern Next.js frontend, RBAC-aware vector search, guardrails, monitoring, document ingestion, and evaluation tooling.

## Why this project exists

- **Problem:** Organizations need accurate answers from private documents without exposing unauthorized data.
- **Solution:** A secure RAG platform that enforces role-based retrieval, applies input/output guardrails, and returns traceable answers with citations.
- **Target users:** teams building internal knowledge assistants, enterprise chatbots, compliance-aware RAG systems.

## What this repository includes

- `backend/` — FastAPI API, RBAC, analytics, logging, MongoDB models, Qdrant integration, guardrails, ingestion, and RAG orchestration.
- `frontend/` — Next.js 16 app with login, chat, documents, evaluations, monitoring, and admin UI.
- `data/` — sample datasets and evaluation fixtures.
- `docs/` — architecture, deployment, API, and RBAC documentation.
- `docker-compose.yml` — local deployment for the full stack.
- `.env.example` — recommended environment variables.

## Key capabilities

- RAG chat with vector retrieval and LLM generation
- JWT-based auth and role-based access controls
- Retrieval-stage RBAC filtering in Qdrant
- Prompt injection, jailbreak, PII, and scope guardrails
- SSE streaming chat support
- Document ingestion for PDF, DOCX, CSV, TXT
- Monitoring and request metrics
- Evaluation pipeline with Ragas

## Architecture diagram

See `docs/ARCHITECTURE.md` for the visual architecture diagram and request lifecycle charts.

## Quick start — local development

### Prerequisites

- Docker Desktop with Compose
- Node.js 20+ and npm
- Python 3.12+ for local backend development
- NVIDIA NIM API key

### Run locally with Docker

```bash
git clone https://github.com/krrish2803/RAG-AI-CHABOT.git
cd "RAG-AI-CHABOT"
cp .env.example .env
# Edit .env and configure your NVIDIA_API_KEY, Qdrant, and JWT settings

docker compose up --build

# Seed sample users and documents
make seed

# Visit the application
# Frontend: http://localhost:3000
# Backend Swagger: http://localhost:8000/docs
```

### Run frontend independently

```bash
cd frontend
npm install
npm run dev
```

### Run backend independently

```bash
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Deploy to GitHub + Netlify

This repository is designed for GitHub source control and Netlify deployment of the frontend.

1. Push the repository to GitHub.
2. Connect Netlify to the GitHub repository.
3. Configure the Netlify site settings:
  - Base directory: `frontend`
  - Build command: `npm install && npm run build`
  - Publish directory: `.next`
  - Branch: `main` (or your default branch)
4. Set Netlify environment variables for frontend only:
  - `NEXT_PUBLIC_API_URL` — your backend API URL, e.g. `https://api.example.com/api/v1`
5. Host the backend separately on a Python-compatible platform (e.g. Railway, Render, Azure, or AWS).

> Note: Netlify is used for the Next.js frontend. The FastAPI backend must be deployed on a separate Python host with a public API endpoint.

## GitHub CI

This repo includes a GitHub Actions workflow at `.github/workflows/ci.yml` that:

- installs Python and Node.js
- installs backend and frontend dependencies
- run Python tests
- builds the frontend

## Folder structure

```text
/
├── backend/                # FastAPI backend services, models, API routes, RAG pipeline
│   ├── app/
│   ├── scripts/            # Seed and maintenance scripts
│   └── requirements.txt
├── frontend/               # Next.js 16 frontend application
│   ├── src/app/            # Pages and routing layers
│   ├── src/lib/            # API client and utilities
│   ├── src/stores/         # Zustand state management
│   └── package.json
├── data/                   # Sample documents and eval datasets
├── docs/                   # Architecture, deployment, and API docs
├── docker-compose.yml      # Local full-stack orchestration
├── netlify.toml            # Netlify frontend deployment config
├── .github/                # GitHub Actions workflows
├── .env.example            # Environment variable template
└── LICENSE                 # Open source license
```

## Environment variables

Copy `.env.example` to `.env` and update values.

Key variables:

- `NVIDIA_API_KEY` — NVIDIA NIM API key
- `QDRANT_API_KEY` — Qdrant API key (cloud or local)
- `JWT_SECRET_KEY` — secure JWT signing key
- `NEXT_PUBLIC_API_URL` — frontend API endpoint
- `FRONTEND_URL` — frontend origin for CORS

## How to use

1. Create a user or use seeded demo users.
2. Login through the frontend.
3. Use the chat interface to ask questions over uploaded documents.
4. Upload documents in the Documents section for new knowledge ingestion.
5. Monitor request metrics and guardrail activity from the monitoring dashboard.
6. Run evaluation jobs from the evaluation panel or backend API.

## Problem / solution summary

**Problem:** Internal knowledge assistants often return answers using unauthorized or outdated content, and they lack enterprise controls for compliance.

**Solution:** This repository provides a guarded enterprise RAG assistant with:

- retrieval-time RBAC filtering in vector search
- injection/jailbreak/PII/scope guardrails
- secure document ingestion with metadata tagging
- monitoring, metrics, and evaluation for trust

## Additional docs

- `docs/ARCHITECTURE.md` — architecture diagrams and flow charts
- `docs/DEPLOYMENT.md` — deployment guide for local Docker and cloud targets
- `docs/API_REFERENCE.md` — API endpoint details
- `docs/RBAC_MATRIX.md` — role and permission mapping

## License

This project is licensed under the MIT License. See `LICENSE`.
