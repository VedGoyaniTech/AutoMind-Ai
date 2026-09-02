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
   pip install -r requirements.txt
   ```
3. Initialize and seed the local database:
   ```bash
   python3 scripts/clean_and_deduplicate_dataset.py
   ```
4. Start the backend development server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## ⚛️ 4. Frontend Setup (Native)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.

---

## 🐳 5. Full-Stack Docker Deployment
Run the entire application stack in Docker:
```bash
# Start MySQL, Backend, and Frontend containers
docker compose up -d --build

# View container logs
docker compose logs -f
```
Services exposed:
- **Frontend:** `http://localhost:5173`
- **Backend API:** `http://localhost:8000` (Swagger docs at `/docs`)
- **MySQL:** `localhost:3307` (`automind_db`)

---

## 🧪 6. Running Tests
Run the complete automated test suite (36+ tests):
```bash
# Inside backend venv or container:
pytest /app/tests -v
```

---

## 🛠️ 7. Common Issues & Troubleshooting
- **Port Conflict (3306 or 8000):** Docker compose maps MySQL to `3307:3306` to prevent conflicts with host databases.
- **Missing Microphone in Chrome on Linux:** Web Speech API requires local media permissions or server fallback. AutoMind AI automatically uses standard `MediaRecorder` audio chunk fallback.
- **SQLite Fallback:** If MySQL is not running, configure `DATABASE_URL=sqlite:///./automind_test.db` in `.env`.
