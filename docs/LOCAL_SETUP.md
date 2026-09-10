# 🚀 AutoMind AI / Project-V — Local Setup & Development Guide

This guide provides reproducible instructions to set up, build, test, and run the AutoMind AI platform on a fresh developer machine.

---

## 📋 1. Prerequisites
- **Operating System:** Linux / macOS / Windows (WSL2 recommended for Windows)
- **Python:** 3.11+
- **Node.js:** v18.0.0 or v20+ (with `npm`)
- **Database:** MySQL 8.0 or local SQLite (built-in fallback)
- **Docker & Docker Compose:** Optional for full-stack containerized deployment

---

## ⚙️ 2. Environment Configuration
Copy the environment template:
```bash
cp .env.example .env
```
Generate production secrets using:
```bash
openssl rand -hex 32
```
And set `APP_SECRET` and `JWT_SECRET` in `.env`.

---

## 🐍 3. Backend Setup (Native)
1. Navigate to backend and create a virtual environment:
   ```bash
   cd backend
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   # Core runtime dependencies
   pip install -r requirements.txt

   # Optional CPU RAG retrieval dependencies
   pip install -r requirements-rag.txt

   # Development & test dependencies
   pip install -r requirements-dev.txt
   ```
3. Validate configuration:
   ```bash
   python scripts/validate_config.py
   ```
4. Run database migrations:
   ```bash
   # Apply all migrations to latest version
   alembic upgrade head

   # To rollback one migration:
   alembic downgrade -1
   ```
5. (Optional in development only) Seed initial test vehicles and dev user:
   ```bash
   APP_ENV=development SEED_DEMO_DATA=true python scripts/seed_db.py
   ```
6. Start the backend development server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## ⚛️ 4. Frontend Setup (Native)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm ci
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.

---

## 🐳 5. Docker Deployment

### A. Local Development (`compose.dev.yml`)
Includes live code hot-reloading and volume mounts:
```bash
docker compose -f compose.dev.yml up -d --build
```
Endpoints:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- MySQL: `localhost:3307`

### B. Hardened Production (`compose.prod.yml`)
Production container topology with:
- Dedicated migration init-container (`alembic upgrade head`)
- Production backend (no `--reload`, unprivileged `appuser`, isolated internal network)
- Nginx reverse proxy frontend (SSE streaming unbuffered, gzip, security headers)
- Private MySQL without exposed host ports
```bash
docker compose -f compose.prod.yml up -d --build
```
Endpoints:
- Web App & API: `http://localhost` (port 80)

---

## 🩺 6. Liveness & Readiness Probes
- **Liveness Probe:** `GET /api/v1/health/live` (Fast check, returns `{"status": "ok"}` without database queries).
- **Readiness Probe:** `GET /api/v1/health/ready` (Validates database connection pool; returns 200 on success, 503 on database disconnect without leaking credentials).
- **General Health:** `GET /api/v1/health` (Sanitized overview for dashboard display).

---

## 🧪 7. Running Tests
Run the complete automated test suite:
```bash
# Inside backend venv or container:
pytest tests -v
```

---

## 🛠️ 8. Common Issues & Troubleshooting
- **Port Conflict (3306 or 8000):** Dev docker compose maps MySQL to `3307:3306` to prevent conflicts with host databases.
- **Production Startup Failure:** Ensure `APP_ENV=production`, valid 32+ char `APP_SECRET` and `JWT_SECRET`, non-default `DATABASE_URL`, and explicit `CORS_ALLOWED_ORIGINS` are set. Validate with `python scripts/validate_config.py`.
- **Database Migrations:** Never use `Base.metadata.create_all()` in production. Always manage schemas with `alembic upgrade head`.

