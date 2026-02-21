# ============================================================
# Social Affiliates Studio - Service Commands
# ============================================================
# Usage:
#   make install      Install all Python + Node dependencies
#   make start        Launch all 4 services (logs → logs/)
#   make stop         Kill all running services
#   make backend      FastAPI backend on :8000
#   make frontend     React/Vite frontend on :5173
#   make orchestrator Autonomous AI orchestrator
#   make dashboard    HITL Flask dashboard on :5000
#   make dirs         Create required data directories
# ============================================================

.PHONY: help install dirs start stop backend frontend orchestrator dashboard

# Default target
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  Ports:  Backend :8000 | Frontend :5173 | Dashboard :5000"

install: ## Install all Python + Node dependencies and create data dirs
	@echo "\033[32m→ Installing Python dependencies...\033[0m"
	pip install -r requirements.txt -q
	@echo "\033[32m→ Installing Node.js dependencies...\033[0m"
	PUPPETEER_SKIP_DOWNLOAD=true npm install --silent
	@$(MAKE) dirs
	@echo "\033[32m✓ Installation complete\033[0m"

dirs: ## Create required data directories
	@mkdir -p logs \
		data/avatars \
		data/content \
		data/media \
		data/posts \
		data/analytics \
		data/strategies \
		data/campaigns \
		output
	@echo "\033[32m✓ Directories ready\033[0m"

backend: ## Start FastAPI backend on :8000
	@echo "\033[34m→ Starting FastAPI backend on :8000\033[0m"
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Start React/Vite frontend on :5173
	@echo "\033[34m→ Starting React frontend on :5173\033[0m"
	npm run frontend:dev

orchestrator: ## Start autonomous AI orchestrator
	@echo "\033[34m→ Starting autonomous orchestrator\033[0m"
	python app.py

dashboard: ## Start HITL Flask dashboard on :5000
	@echo "\033[34m→ Starting HITL dashboard on :5000\033[0m"
	python dashboard/server.py

start: dirs ## Launch all 4 services (logs written to logs/)
	@bash start.sh

stop: ## Kill all running services
	@echo "\033[31m→ Stopping all services...\033[0m"
	@-pkill -f "uvicorn main:app" 2>/dev/null || true
	@-pkill -f "vite" 2>/dev/null || true
	@-pkill -f "python app\.py" 2>/dev/null || true
	@-pkill -f "dashboard/server\.py" 2>/dev/null || true
	@-rm -f .pids 2>/dev/null || true
	@echo "\033[31m✓ All services stopped\033[0m"

env-check: ## Verify .env has the required keys set
	@python3 -c "\
import os; from dotenv import load_dotenv; load_dotenv(); \
missing = [k for k in ['OPENAI_API_KEY','JWT_SECRET_KEY'] if not os.getenv(k)]; \
print('\033[31mMissing keys: ' + ', '.join(missing) + '\033[0m') if missing \
else print('\033[32m✓ Required env vars are set\033[0m')"
