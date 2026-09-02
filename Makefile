.PHONY: help setup-backend setup-frontend test-backend build-frontend run-docker stop-docker smoke-test clean

help:
	@echo "AutoMind AI Platform — Build & Run Commands:"
	@echo "  make setup-backend   - Install backend requirements"
	@echo "  make setup-frontend  - Install frontend dependencies"
	@echo "  make test-backend    - Run all backend pytest test suites"
	@echo "  make build-frontend  - Compile and build frontend production bundle"
	@echo "  make run-docker      - Start MySQL, Backend, and Frontend containers"
	@echo "  make stop-docker     - Stop all Docker containers"
	@echo "  make smoke-test      - Run end-to-end API smoke tests"
	@echo "  make clean           - Remove temporary caches and safe build artifacts"

setup-backend:
	cd backend && pip install -r requirements.txt

setup-frontend:
	cd frontend && npm install

test-backend:
	cd backend && pytest tests -v

build-frontend:
	cd frontend && npm run build

run-docker:
	docker compose up -d --build

stop-docker:
	docker compose down

smoke-test:
	python3 -c "import urllib.request; resp = urllib.request.urlopen('http://localhost:8000/api/v1/health'); print('Backend Health:', resp.getcode())"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf frontend/dist
