# Development Guide

## Local setup (without Docker for API)

```bash
# Terminal 1 — database
docker compose up db -d

# Terminal 2 — backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=postgresql+asyncpg://aidevconnect:aidevconnect@localhost:5432/aidevconnect
export CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
alembic upgrade head
python scripts/seed_demo.py
uvicorn app.main:app --reload

# Terminal 3 — frontend
cd frontend
npm install
npm run dev
```

## API testing (Swagger)

1. Open http://localhost:8000/docs
2. Register two users via `POST /api/v1/auth/register`
3. Login via `POST /api/v1/auth/login/json` — copy `access_token`
4. Click **Authorize** → `Bearer <token>`
5. Create projects, find matches, send match requests

## WebSocket testing

```bash
websocat "ws://localhost:8000/api/v1/ws?token=<access_token>"
```

Events: `match_request`, `match_accepted`, `match_rejected`

## Scripts

| Script | Purpose |
|--------|---------|
| `backend/scripts/seed_demo.py` | Portfolio demo users (alice, bob, carol) |
| `backend/scripts/seed_load_test.py` | 500 projects for Locust |
| `scripts/run_load_test.sh` | Full load test with p95 assertion |

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
alembic upgrade head
pytest -v
ruff check app tests scripts
```

## Production checklist

- [ ] `ENVIRONMENT=production`
- [ ] `SECRET_KEY` — random 32+ character string
- [ ] `MOCK_EMBEDDINGS=false` + valid `OPENAI_API_KEY`
- [ ] `CORS_ORIGINS` — your frontend URL only
- [ ] Deploy and verify `/health` shows `"embedding_mode": "openai"`
- [ ] Run load test, screenshot p95 for resume
