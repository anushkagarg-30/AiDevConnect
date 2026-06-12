# Architecture

## Request flow — semantic matching

1. User submits a project (title + description + skills)
2. Backend concatenates fields and calls OpenAI `text-embedding-3-small`
3. 1536-dimensional vector stored in `projects.embedding` (pgvector column)
4. ivfflat index accelerates cosine-distance queries
5. `GET /projects/{id}/matches` runs:

```sql
SELECT *, 1 - (embedding <=> $1) AS similarity
FROM projects
WHERE user_id != $2
ORDER BY embedding <=> $1
LIMIT 10;
```

## WebSocket notifications

`ConnectionManager` maintains `{user_id: WebSocket}`. On match create/accept/reject, the API pushes JSON events to the relevant user's open connection.

## Security

- JWT bearer tokens for REST; WebSocket auth via query param (document tradeoffs in interviews)
- CORS restricted to configured origins (no wildcard in production)
- Production startup fails if `SECRET_KEY` is a known dev default
- Passwords hashed with bcrypt

## Performance

Locust load test in CI: 50 concurrent users, 30s duration, p95 < 200ms on matching endpoint with 500 seeded projects and ivfflat index.
