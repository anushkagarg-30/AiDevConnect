#!/usr/bin/env bash
# AI DevConnect — portfolio setup script
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

echo ""
echo "========================================"
echo "  AI DevConnect — Portfolio Setup"
echo "========================================"
echo ""

# --- Prerequisites ---
echo "Checking prerequisites..."
echo ""

MISSING=0

if command -v git >/dev/null 2>&1; then
  ok "Git $(git --version | awk '{print $3}')"
else
  fail "Git not found. Install Xcode Command Line Tools: xcode-select --install"
fi

if command -v node >/dev/null 2>&1; then
  ok "Node $(node --version)"
else
  warn "Node not found — install from https://nodejs.org"
  MISSING=1
fi

if command -v python3 >/dev/null 2>&1; then
  ok "Python $(python3 --version | awk '{print $2}')"
else
  warn "Python 3 not found"
  MISSING=1
fi

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  ok "Docker $(docker --version | awk '{print $3}' | tr -d ',')"
elif [ -d "/Applications/Docker.app" ]; then
  warn "Docker is installed but not running — open Docker Desktop from Applications"
  MISSING=1
else
  warn "Docker Desktop not installed"
  echo ""
  echo "  Install Docker Desktop (required for easiest setup):"
  echo "  https://www.docker.com/products/docker-desktop/"
  echo ""
  MISSING=1
fi

echo ""

# --- Environment file ---
if [ ! -f .env ]; then
  cp .env.example .env
  ok "Created .env from .env.example"
else
  ok ".env already exists"
fi

# --- Install frontend deps ---
if [ -d frontend/node_modules ]; then
  ok "Frontend dependencies already installed"
else
  echo "Installing frontend dependencies..."
  (cd frontend && npm install)
  ok "Frontend dependencies installed"
fi

# --- Install backend deps ---
if [ -d backend/.venv ]; then
  ok "Backend virtualenv already exists"
else
  echo "Creating backend virtualenv..."
  python3 -m venv backend/.venv
  ok "Backend virtualenv created"
fi

echo "Installing backend dependencies..."
backend/.venv/bin/pip install -q -r backend/requirements-dev.txt
ok "Backend dependencies installed"

echo ""

if [ "$MISSING" -ne 0 ]; then
  echo "========================================"
  warn "Install Docker Desktop, then run this script again."
  echo ""
  echo "  After Docker is running:"
  echo "    ./scripts/setup-portfolio.sh"
  echo "    docker compose up --build"
  echo ""
  echo "  Then open: http://localhost:5173"
  echo "========================================"
  exit 1
fi

# --- Start services ---
echo "Starting all services (first run builds images — may take a few minutes)..."
echo ""
docker compose up --build -d

echo ""
echo "Waiting for API to be ready..."
for i in $(seq 1 60); do
  if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "{}")
echo ""
echo "========================================"
echo -e "${GREEN}  Setup complete!${NC}"
echo "========================================"
echo ""
echo "  App:      http://localhost:5173"
echo "  API docs: http://localhost:8000/docs"
echo "  Health:   http://localhost:8000/health"
echo ""
echo "  Health response: $HEALTH"
echo ""
echo "  Demo login:"
echo "    alice@demo.com / demo1234"
echo "    bob@demo.com   / demo1234"
echo ""
echo "  Test flow:"
echo "    1. Log in as Alice"
echo "    2. Projects → Find matches → Connect"
echo "    3. Incognito → log in as Bob → see notification → Accept"
echo ""
echo "  Stop services:  docker compose down"
echo "  View logs:      docker compose logs -f"
echo "========================================"
echo ""
