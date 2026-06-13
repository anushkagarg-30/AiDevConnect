# Database setup (pgvector)

AI DevConnect requires **PostgreSQL with the pgvector extension** so project embeddings (1536-dim vectors) can be stored and searched with cosine distance.

## Local development (Docker)

`docker compose up` starts an official **pgvector/pgvector:pg16** container with:

- Persistent volume `pgdata` (data survives restarts)
- `backend/docker/init-db.sql` enables the `vector` extension on first boot
- Alembic migrations create tables + ivfflat index

Verify:

```bash
curl http://localhost:8000/health
```

Expect `"database": "connected"` and `"pgvector": "enabled"`.

---

## Production — Neon (recommended)

Render’s free Postgres **expires after 30 days**. For a permanent portfolio demo, use **[Neon](https://neon.tech)** (free tier, pgvector included).

### 1. Create a Neon project

1. Sign up at https://neon.tech
2. **New project** → name e.g. `aidevconnect`
3. Region: pick one close to your Render API (e.g. `US West` if API is on Render Oregon)

### 2. Enable pgvector

In the Neon SQL editor (or any client), run once:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

(Neon supports pgvector on all plans.)

### 3. Copy the connection string

Neon dashboard → **Connect** → use the **Direct** connection (not **Pooled**):

```
postgresql://USER:PASSWORD@ep-....us-east-1.aws.neon.tech/neondb?sslmode=require
```

Use the hostname **without** `-pooler` for migrations and this API. The app strips `sslmode` from the URL and configures SSL for asyncpg automatically.

The app auto-converts `postgresql://` → `postgresql+asyncpg://` in config.

### 4. Wire Render API to Neon

In **Render** → **aidevconnect-api** → **Environment**:

| Key | Value |
|-----|--------|
| `DATABASE_URL` | Your Neon connection string (paste full URL) |
| `GOOGLE_API_KEY` | Your Gemini key |
| `MOCK_EMBEDDINGS` | `false` |
| `EMBEDDING_PROVIDER` | `gemini` |

Remove or ignore the old Render Postgres `DATABASE_URL` if the blueprint still linked one.

**Manual deploy** — migrations and demo seed run on startup via `scripts/start.sh`.

### 5. Verify production

```bash
curl https://aidevconnect-api.onrender.com/health
```

```json
{
  "status": "ok",
  "database": "connected",
  "pgvector": "enabled",
  "embedding_mode": "gemini",
  "match_min_similarity": 0.72
}
```

---

## What gets stored

| Table | Purpose |
|-------|---------|
| `users` | Accounts (JWT auth) |
| `projects` | Title, description, skills + **`embedding vector(1536)`** |
| `match_requests` | Collaboration requests between projects |

Matching query (core of the project):

```sql
SELECT *, 1 - (embedding <=> $1) AS similarity
FROM projects
WHERE user_id != $2
ORDER BY embedding <=> $1
LIMIT 10;
```

Demo projects are **re-embedded with Gemini** on each API startup so vectors stay consistent with the active embedding provider.

---

## Alternatives

| Option | Pros | Cons |
|--------|------|------|
| **Neon** | Free, permanent, pgvector | External service (one-time setup) |
| **Render Postgres** | Blueprint auto-wires URL | Free tier expires in 30 days |
| **Local Docker pgvector** | Full stack offline | Not hosted for portfolio URL |

SQLite / embedded DBs are **not supported** — this project relies on pgvector-specific operators (`<=>`, ivfflat).
