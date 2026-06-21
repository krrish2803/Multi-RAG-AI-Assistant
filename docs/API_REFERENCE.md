# API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs available at: `http://localhost:8000/docs`

## Authentication

### POST /auth/login

Authenticate and receive JWT tokens.

**Request:**
```json
{
  "email": "admin@company.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### POST /auth/register

Register a new user.

**Request:**
```json
{
  "email": "new@company.com",
  "password": "password123",
  "full_name": "New User",
  "role": "employee",
  "departments": ["engineering"]
}
```

### POST /auth/refresh

Refresh an expired access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### GET /auth/me

Get current user profile. Requires JWT.

**Response:**
```json
{
  "id": "665...",
  "email": "admin@company.com",
  "full_name": "Admin User",
  "role": "admin",
  "departments": [],
  "is_active": true,
  "created_at": "2025-01-01T00:00:00"
}
```

## Chat

### POST /chat/send

Send a message and get RAG-powered response. Requires JWT.

**Request:**
```json
{
  "message": "What are the company's work hours?",
  "conversation_id": "optional-existing-id"
}
```

**Response:**
```json
{
  "response": "The company's standard work hours are 9:00 AM to 5:00 PM...",
  "conversation_id": "665...",
  "sources": [
    {
      "filename": "company_policy.txt",
      "department": "company-wide",
      "chunk_index": 0,
      "score": 0.89,
      "content_snippet": "Standard work hours are 9:00 AM..."
    }
  ],
  "blocked": false,
  "block_reason": null,
  "latency_ms": 1234
}
```

### POST /chat/send/stream

SSE streaming version of chat. Same request, returns `text/event-stream`.

### GET /chat/conversations

List all conversations for current user.

### GET /chat/conversations/{id}

Get all messages in a conversation.

### DELETE /chat/conversations/{id}

Delete a conversation and its messages.

## Documents

### POST /documents/upload

Upload a document for ingestion. Requires JWT.

**Form data:**
- `file`: File (PDF, DOCX, TXT, CSV)
- `department`: string (company-wide, hr, finance, marketing, engineering)
- `sensitivity`: string (public, internal, confidential, restricted)

### GET /documents

List documents with optional filters.

**Query params:** `department`, `status`, `skip`, `limit`

### GET /documents/{id}

Get a specific document.

### DELETE /documents/{id}

Delete document and embeddings. Admin only.

## Users (Admin)

### GET /users

List all users. Admin only.

### PUT /users/{id}/role

Update user role/departments. Admin only.

**Request:**
```json
{
  "role": "hr",
  "departments": ["hr"],
  "is_active": true
}
```

### DELETE /users/{id}

Delete a user. Admin only.

## Monitoring

### GET /monitoring/summary

Get monitoring summary. Requires admin/executive role.

**Query params:** `days` (default: 7)

**Response:**
```json
{
  "total_requests": 150,
  "avg_latency_ms": 1234.5,
  "total_tokens": 45000,
  "total_cost_usd": 0.0342,
  "guardrail_triggers": 3,
  "error_count": 2
}
```

### GET /monitoring/costs

Cost breakdown by role. Requires admin/executive role.

### GET /monitoring/errors

Recent error summary. Requires admin/executive role.

### GET /monitoring/guardrails

Guardrail trigger summary. Requires admin/executive role.

### GET /monitoring/requests

List recent request metrics.

## Evaluation

### POST /evaluation/run

Trigger a new evaluation run. Requires admin/engineering/executive role.

**Request:**
```json
{
  "dataset_name": "default",
  "run_name": "optional-name"
}
```

### GET /evaluation/runs

List evaluation runs.

### GET /evaluation/results/{run_id}

Get results for a specific evaluation run.

## Health

### GET /health

Basic health check.

### GET /readiness

Detailed readiness check for MongoDB and Qdrant.
