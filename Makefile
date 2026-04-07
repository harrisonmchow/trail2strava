.PHONY: dev frontend backend install

dev:
	@echo "Starting frontend and backend..."
	@make -j2 frontend backend

frontend:
	cd frontend && npm run dev

backend:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

install:
	cd backend && source venv/bin/activate && pip install -r requirements.txt && playwright install chromium
	cd frontend && npm install
