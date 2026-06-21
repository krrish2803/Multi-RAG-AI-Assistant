# RBAC Matrix

## Role Definitions

| Role | Description |
|------|-------------|
| **employee** | Base access to company-wide public/internal documents |
| **hr** | Human Resources — access to HR documents including confidential |
| **finance** | Finance department — access to financial documents including confidential |
| **marketing** | Marketing — access to marketing materials (public/internal only) |
| **engineering** | Engineering — access to technical docs including confidential |
| **executive** | Full access to all departments and sensitivity levels |
| **admin** | System administrator — full access + ingestion + user management |

## Department Access Matrix

| Role | company-wide | hr | finance | marketing | engineering |
|------|:---:|:---:|:---:|:---:|:---:|
| employee | ✅ | ❌ | ❌ | ❌ | ❌ |
| hr | ✅ | ✅ | ❌ | ❌ | ❌ |
| finance | ✅ | ❌ | ✅ | ❌ | ❌ |
| marketing | ✅ | ❌ | ❌ | ✅ | ❌ |
| engineering | ✅ | ❌ | ❌ | ❌ | ✅ |
| executive | ✅ | ✅ | ✅ | ✅ | ✅ |
| admin | ✅ | ✅ | ✅ | ✅ | ✅ |

## Sensitivity Access Matrix

| Role | public | internal | confidential | restricted |
|------|:---:|:---:|:---:|:---:|
| employee | ✅ | ✅ | ❌ | ❌ |
| hr | ✅ | ✅ | ✅ | ❌ |
| finance | ✅ | ✅ | ✅ | ❌ |
| marketing | ✅ | ✅ | ❌ | ❌ |
| engineering | ✅ | ✅ | ✅ | ❌ |
| executive | ✅ | ✅ | ✅ | ✅ |
| admin | ✅ | ✅ | ✅ | ✅ |

## API Endpoint Access

| Endpoint | Roles |
|----------|-------|
| POST /auth/login | Public |
| POST /auth/register | Public |
| GET /auth/me | All authenticated |
| POST /chat/send | All authenticated |
| POST /documents/upload | All authenticated |
| GET /documents | All authenticated |
| DELETE /documents/{id} | admin |
| GET /users | admin |
| PUT /users/{id}/role | admin |
| GET /monitoring/* | admin, executive |
| POST /evaluation/run | admin, engineering, executive |

## Retrieval Filter Example

When a user with role `engineering` searches, the Qdrant filter is:

```json
{
  "must": [
    {
      "key": "department",
      "match": { "any": ["company-wide", "engineering"] }
    },
    {
      "key": "sensitivity",
      "match": { "any": ["public", "internal", "confidential"] }
    }
  ]
}
```

This means:
- Only chunks from `company-wide` OR `engineering` department docs are retrieved
- Only chunks with `public`, `internal`, or `confidential` sensitivity are returned
- HR, Finance, Marketing docs are invisible at the retrieval level
- Restricted documents are never returned to non-executive users

## Enforcement Layers

1. **API Layer**: Route-level role checks prevent unauthorized access to endpoints
2. **Retrieval Layer**: Qdrant metadata filters ensure only authorized chunks are retrieved
3. **Output Layer**: PII detection and redaction prevents accidental data leakage in responses
