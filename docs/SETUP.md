# Portfolio Setup Guide

Follow these steps in order. Total time: ~45 minutes first time.

---

## Step 1 — Install Docker Desktop (required)

This project uses PostgreSQL + **pgvector**. Docker is the easiest way to run it.

1. Download: https://www.docker.com/products/docker-desktop/
2. Install and **open Docker Desktop**
3. Wait until the whale icon in the menu bar says **"Docker Desktop is running"**

Verify in terminal:
```bash
docker --version
docker info
```

---

## Step 2 — Run the setup script

```bash
cd /Users/anushkagarg/AiDevConnect
chmod +x scripts/setup-portfolio.sh
./scripts/setup-portfolio.sh
```

This will:
- Check Git, Node, Python, Docker
- Create `.env` if missing
- Install frontend + backend dependencies
- Start all services with demo data seeded

---

## Step 3 — Verify the app works

Open these URLs:

| URL | What to check |
|-----|---------------|
| http://localhost:5173 | Login page loads |
| http://localhost:8000/health | `{"status":"ok","database":"connected",...}` |
| http://localhost:8000/docs | Swagger UI loads |

### Demo test (do this once)

1. Go to http://localhost:5173
2. Log in: **alice@demo.com** / **demo1234**
3. Click **Projects** → **Find matches** on Alice's project
4. Bob's project should appear with a **% match** score
5. Click **Connect**
6. Open a **private/incognito window**
7. Log in: **bob@demo.com** / **demo1234**
8. See the toast notification → **Matches** → **Accept**

If all of that works, your portfolio demo is ready.

---

## Step 4 — Load test (for resume bullet)

```bash
./scripts/run_load_test.sh
```

Screenshot the line showing **p95** (e.g. `p95: 47.2ms`). Use that exact number on your resume.

---

## Step 5 — Screenshots

Take 3 screenshots and save to `docs/screenshots/`:

1. `dashboard.png` — logged-in dashboard
2. `matches.png` — match results with similarity %
3. `notifications.png` — toast notification

Then add to README:
```markdown
![Dashboard](docs/screenshots/dashboard.png)
![Matches](docs/screenshots/matches.png)
```

---

## Step 6 — Push to GitHub

```bash
# Create repo on GitHub first: github.com/new → name it AiDevConnect

cd /Users/anushkagarg/AiDevConnect
git add .
git commit -m "Initial commit: AI DevConnect portfolio project"
git remote add origin https://github.com/YOUR_USERNAME/AiDevConnect.git
git push -u origin main
```

Replace `YOUR_USERNAME` in README CI badge too.

---

## Step 7 — Deploy live demo (optional but recommended)

1. Create a **Neon** database with pgvector — see [DATABASE.md](DATABASE.md)
2. Go to https://dashboard.render.com/
3. **New** → **Blueprint** → connect your GitHub repo
4. Set **DATABASE_URL** (Neon) and **GOOGLE_API_KEY** when prompted
5. Wait for deploy (~10 min; demo seed runs automatically)
6. Verify `https://your-api.onrender.com/health` shows `pgvector: enabled`
7. Add live URLs to README

---

## Troubleshooting

### "Docker not found"
Install Docker Desktop and make sure it's **running** before `docker compose up`.

### Port already in use
```bash
lsof -i :5173 -i :8000 -i :5432
# Kill the process or change ports in docker-compose.yml
```

### API won't start
```bash
docker compose logs api
```
Usually a DB connection issue — wait for postgres health check, then retry:
```bash
docker compose down && docker compose up --build
```

### Frontend can't reach API
Make sure you're using http://localhost:5173 (not 127.0.0.1 with mismatched CORS). Both are in `.env` CORS_ORIGINS.

### Reset everything
```bash
docker compose down -v   # deletes database volume
docker compose up --build
```

---

## Daily commands

| Task | Command |
|------|---------|
| Start | `docker compose up` |
| Start in background | `docker compose up -d` |
| Stop | `docker compose down` |
| View logs | `docker compose logs -f api` |
| Re-seed demo users | `docker compose exec api python scripts/seed_demo.py` |

---

## Resume bullet template

After load test, fill in your actual p95:

> Built a developer networking platform (FastAPI, React, PostgreSQL + pgvector) with OpenAI embeddings for semantic project matching and WebSocket notifications; achieved **XXms p95** on similarity search under 50 concurrent users, verified in GitHub Actions CI.
