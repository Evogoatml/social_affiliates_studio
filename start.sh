#!/usr/bin/env bash
# ============================================================
# Social Affiliates Studio - Start All Services
# ============================================================
# Starts 4 services in parallel, writes logs to logs/
# Press Ctrl+C to stop everything cleanly.
# ============================================================

set -euo pipefail

# ── Colors ───────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Paths ────────────────────────────────────────────────────
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT/logs"
PID_FILE="$ROOT/.pids"

mkdir -p "$LOG_DIR"

# ── Cleanup on exit ──────────────────────────────────────────
cleanup() {
    echo -e "\n${RED}${BOLD}→ Shutting down all services...${NC}"
    if [[ -f "$PID_FILE" ]]; then
        while IFS= read -r pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    echo -e "${RED}✓ All services stopped${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# ── Guard: .env must exist ───────────────────────────────────
if [[ ! -f "$ROOT/.env" ]]; then
    echo -e "${RED}✗ .env not found. Run: cp config/.env.example .env${NC}"
    exit 1
fi

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════╗"
echo "║      Social Affiliates Studio                ║"
echo "║      Starting all services...                ║"
echo "╚══════════════════════════════════════════════╝${NC}"
echo ""

# ── Helper: start a service ──────────────────────────────────
start_service() {
    local name="$1"
    local log="$LOG_DIR/$2.log"
    local cmd="${@:3}"

    echo -e "${CYAN}→ Starting ${BOLD}${name}${NC}${CYAN}...${NC}"
    echo "  Log: $log"

    # Run from project root
    cd "$ROOT"
    eval "$cmd" >> "$log" 2>&1 &
    local pid=$!
    echo "$pid" >> "$PID_FILE"
    echo -e "${GREEN}  ✓ PID $pid${NC}"
    echo ""
}

# ── Start services ───────────────────────────────────────────

# 1. FastAPI Backend (:8000)
start_service \
    "FastAPI Backend  :8000" \
    "backend" \
    "cd '$ROOT/backend' && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

# 2. React Frontend (:5173)
start_service \
    "React Frontend   :5173" \
    "frontend" \
    "cd '$ROOT' && npm run frontend:dev"

# 3. HITL Dashboard (:5000)
start_service \
    "HITL Dashboard   :5000" \
    "dashboard" \
    "cd '$ROOT' && python dashboard/server.py"

# 4. Autonomous Orchestrator
start_service \
    "Orchestrator     (background)" \
    "orchestrator" \
    "cd '$ROOT' && python app.py"

# ── Wait for backend to be ready ────────────────────────────
echo -e "${YELLOW}→ Waiting for backend on :8000...${NC}"
for i in $(seq 1 20); do
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend ready${NC}"
        break
    fi
    sleep 1
done

# ── Summary ─────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}"
echo "╔══════════════════════════════════════════════╗"
echo "║  All services launched                       ║"
echo "║                                              ║"
echo "║  Backend API  →  http://localhost:8000       ║"
echo "║  API Docs     →  http://localhost:8000/docs  ║"
echo "║  Frontend     →  http://localhost:5173       ║"
echo "║  Dashboard    →  http://localhost:5000       ║"
echo "║                                              ║"
echo "║  Logs:  ./logs/                              ║"
echo "║  Stop:  Ctrl+C  or  make stop               ║"
echo "╚══════════════════════════════════════════════╝${NC}"
echo ""

# ── Tail all logs ────────────────────────────────────────────
echo -e "${YELLOW}── Live logs (Ctrl+C to stop all) ────────────────${NC}"
tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log" \
         "$LOG_DIR/dashboard.log" "$LOG_DIR/orchestrator.log" \
    2>/dev/null &
TAIL_PID=$!
echo "$TAIL_PID" >> "$PID_FILE"

# Wait forever until interrupted
wait
