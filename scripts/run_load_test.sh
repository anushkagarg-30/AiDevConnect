#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${LOAD_TEST_HOST:-http://localhost:8000}"
USERS="${LOAD_TEST_USERS:-50}"
SPAWN_RATE="${LOAD_TEST_SPAWN_RATE:-10}"
DURATION="${LOAD_TEST_DURATION:-30s}"
P95_MAX_MS="${LOAD_TEST_P95_MAX_MS:-200}"
PROJECTS="${LOAD_TEST_PROJECTS:-500}"

export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://aidevconnect:aidevconnect@localhost:5432/aidevconnect}"
export MOCK_EMBEDDINGS="${MOCK_EMBEDDINGS:-true}"
export SECRET_KEY="${SECRET_KEY:-load-test-secret}"

cd "$ROOT/backend"
python -m alembic upgrade head
python scripts/seed_load_test.py --projects "$PROJECTS"

mkdir -p "$ROOT/loadtests/results"

if ! curl -sf "$HOST/health" >/dev/null 2>&1; then
  echo "Starting API on $HOST ..."
  uvicorn app.main:app --host 0.0.0.0 --port 8000 &
  API_PID=$!
  trap 'kill $API_PID 2>/dev/null || true' EXIT
  for _ in $(seq 1 30); do
    curl -sf "$HOST/health" >/dev/null && break
    sleep 1
  done
fi

cd "$ROOT"
locust -f loadtests/locustfile.py \
  --headless \
  -u "$USERS" \
  -r "$SPAWN_RATE" \
  -t "$DURATION" \
  --host "$HOST" \
  --csv=loadtests/results/locust \
  --only-summary

STATS_FILE="loadtests/results/locust_stats.csv"
if [[ ! -f "$STATS_FILE" ]]; then
  echo "Locust stats file not found: $STATS_FILE"
  exit 1
fi

python3 - <<PY
import csv
import sys

p95_max = int("${P95_MAX_MS}")
target = "/api/v1/projects/[id]/matches"

with open("${STATS_FILE}") as f:
    rows = list(csv.DictReader(f))

match_row = next((r for r in rows if r.get("Name") == target), None)
if not match_row:
    print(f"Could not find stats for {target}")
    sys.exit(1)

p95 = float(match_row["95%"])
avg = float(match_row["Average Response Time"])
rps = float(match_row["Requests/s"])
print(f"Matching endpoint — avg: {avg:.1f}ms  p95: {p95:.1f}ms  rps: {rps:.1f}")

if p95 > p95_max:
    print(f"FAIL: p95 {p95:.1f}ms exceeds {p95_max}ms threshold")
    sys.exit(1)

print(f"PASS: p95 {p95:.1f}ms is under {p95_max}ms")
PY
