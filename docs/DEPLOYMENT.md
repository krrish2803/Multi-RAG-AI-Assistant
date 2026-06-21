# Deployment Guide

## Local Docker Deployment

### Prerequisites
- Docker Desktop with Docker Compose v2
- NVIDIA NIM API key

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/krrish2803/RAG-AI-CHABOT.git
cd "RAG-AI-CHABOT"

# 2. Configure environment
cp .env.example .env
# Edit .env and set NVIDIA_API_KEY

# 3. Start services
docker compose up -d

# 4. Wait for health checks (30-60 seconds)
docker compose ps

# 5. Seed data
make seed

# 6. Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Stopping

```bash
make down          # Stop services
make clean         # Stop + remove volumes (deletes all data)
```

## GitHub Repository Deployment

1. Push the repository to GitHub.
2. Protect the default branch with required status checks if desired.
3. Use GitHub Actions to verify changes before merge.

### Recommended workflow

1. Create a feature branch.
2. Open a pull request.
3. Confirm CI passes.
4. Merge to `main`.

## Netlify Frontend Deployment

Netlify is a strong fit for the frontend. The backend must be hosted separately on a Python-compatible service.

### Netlify site setup

- Repository: connect the GitHub repo.
- Base directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `.next`
- Branch to deploy: `main`

### Required frontend environment variables

- `NEXT_PUBLIC_API_URL` — public backend API URL, e.g. `https://api.example.com/api/v1`
- `FRONTEND_URL` — Netlify site URL (or custom domain)

### Optional Netlify config

This repository includes `netlify.toml` for Netlify build configuration.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVIDIA_API_KEY` | Yes | NVIDIA NIM API key |
| `JWT_SECRET_KEY` | Yes (prod) | Random 64-char string for JWT signing |
| `MONGO_PASSWORD` | Yes (prod) | MongoDB root password |
| `QDRANT_API_KEY` | Yes (prod) | Qdrant API key |
| `NVIDIA_CHAT_MODEL` | No | Default: meta/llama-3.1-70b-instruct |
| `NVIDIA_EMBED_MODEL` | No | Default: nvidia/nv-embedqa-e5-v5 |
| `LOG_LEVEL` | No | Default: INFO. Use DEBUG for development |

## Azure Deployment Plan

### Architecture

```
Azure Front Door / Application Gateway
    ├── Azure App Service (Frontend - Next.js)
    ├── Azure Container Instance / AKS (Backend - FastAPI)
    ├── Azure Cosmos DB (MongoDB API)
    ├── Azure Container Instance (Qdrant)
    └── Azure Key Vault (secrets)
```

### Steps

1. **Create Resource Group**
```bash
az group create --name rag-assistant --location eastus
```

2. **Deploy Cosmos DB (MongoDB API)**
```bash
az cosmosdb create --name rag-cosmos --resource-group rag-assistant --kind MongoDB
```

3. **Deploy Qdrant on ACI**
```bash
az container create --name rag-qdrant --resource-group rag-assistant \
  --image qdrant/qdrant:v1.10.0 --ports 6333 6334
```

4. **Deploy Backend to App Service**
```bash
az webapp create --name rag-backend --resource-group rag-assistant \
  --plan rag-plan --deployment-container-image-name <your-image>
```

5. **Deploy Frontend to Vercel or App Service**
```bash
cd frontend && vercel deploy --prod
```

### Production Hardening Checklist

- [ ] Use Azure Key Vault for all secrets
- [ ] Enable HTTPS/TLS for all services
- [ ] Set up VNet for network isolation
- [ ] Configure Cosmos DB with private endpoint
- [ ] Enable Azure Monitor + Application Insights
- [ ] Set up alerting for errors and latency spikes
- [ ] Configure auto-scaling for backend
- [ ] Enable Cosmos DB backup and point-in-time restore
- [ ] Set up CI/CD pipeline (GitHub Actions / Azure DevOps)
- [ ] Add rate limiting to API gateway
- [ ] Configure CORS for production frontend domain only
- [ ] Enable WAF (Web Application Firewall)
- [ ] Review and rotate all default credentials
- [ ] Set up log aggregation (Azure Log Analytics)
- [ ] Configure RBAC at Azure resource level

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB health check fails | Check MONGO_URI and credentials in .env |
| Qdrant connection refused | Ensure port 6333 is not blocked |
| NVIDIA API errors | Verify NVIDIA_API_KEY is valid |
| Frontend can't reach backend | Check NEXT_PUBLIC_API_URL in .env |
| Ingestion fails | Check backend logs: `make logs` |
