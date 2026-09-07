# AutoMind AI — Intelligent Automobile Intelligence & Research Platform

**AutoMind AI** is an enterprise-grade full-stack automotive research and intelligence platform. It features a fine-tuned multilingual LLM (Qwen2.5-1.5B with LoRA adapters and 4-bit edge quantization), a high-performance Hybrid RAG engine (dense FAISS embeddings + SQL filters), a deterministic City-Wise RTO & Reducing-Balance Loan EMI calculation engine, Web Speech voice input, rich vehicle media galleries, and an offline DPO (Direct Preference Optimization) feedback collection pipeline.

---

## 🌟 Key Platform Capabilities

### 1. 🚗 City-Wise RTO, On-Road Price & Reducing-Balance Loan EMI Engine
- **Deterministic Pricing Calculation**:
  $$\text{On-Road Price} = \text{Ex-Showroom} + \text{State RTO Tax} + \text{Insurance (1+3 Yr)} + \text{1\% TCS} + \text{FASTag} + \text{HSRP/Cess}$$
- **State Tax Slabs Supported**:
  - **Gujarat (`GJ`)**: 6% Road Tax across price bands, 0% EV exemption.
  - **Maharashtra (`MH`)**: Progressive 11%–13% Petrol, 13%–15% Diesel, 0.5% Road Safety Cess.
  - **Delhi (`DL`)**: Tiered 4%–10% Petrol, 5%–12.5% Diesel, 0% EV waiver.
  - **Karnataka (`KA`)**: 13%–18% Road Tax + 11% Infrastructure Cess.
- **Reducing-Balance EMI Equation**:
  $$EMI = P \times r \times \frac{(1+r)^n}{(1+r)^n - 1}$$
  Supports multi-tenure (3, 5, 7 years) comparison, zero-interest safety, and down-payment validations.
- **Dedicated APIs**:
  - `POST /api/v1/pricing/quote`: Comprehensive on-road breakdown + 3/5/7-yr EMI matrix.
  - `POST /api/v1/pricing/on-road`: Itemized on-road tax breakdown.
  - `POST /api/v1/pricing/emi`: Standalone multi-tenure loan calculator.

### 2. 🎙️ Web Speech Voice Input & Multi-Modal Vehicle Media Gallery
- **Web Speech API**: Browser-based speech recognition with fallback to `webkitSpeechRecognition`.
- **Languages**: Hindi (`hi-IN`), Gujarati (`gu-IN`), English India (`en-IN`) with language toggle and `localStorage` persistence.
- **Rich Vehicle Media Cards**: Responsive 16:9 carousel with exterior, interior, category filtering, captions, lazy loading, and touch swipe.

### 3. 👍 User Feedback API & Offline DPO Dataset Exporter
- **User Feedback Controls**: Thumbs Up / Thumbs Down below completed assistant messages.
- **Reason Code Dialog**: Reports incorrect price/RTO, not relevant, incomplete, or language issues.
- **APIs**: `POST /api/v1/chat/feedback`, `PATCH`, `DELETE`, `GET /status`.
- **Offline DPO Exporter (`ml/datasets/export_dpo_dataset.py`)**:
  - Strict ML correctness: Only creates DPO pairs when matching prompts have both a chosen (`up`) and rejected (`down`) response.
  - Redacts PII (emails, phone numbers).
  - Exports validated JSONL to `ml/datasets/dpo_preference_dataset.jsonl`.

### 4. ⚡ 4-Bit Model Quantization & Low-Latency Inference
- **Target Formats**: GGUF (Q4_K_M) via `llama.cpp` and BitsAndBytes NF4.
- **Memory Optimization**: VRAM footprint reduced from 3.8 GB to 1.25 GB (67.1% memory saving).
- **Benchmark Harness (`ml/inference/benchmark_inference.py`)**:
  - Measures TTFT (Time to First Token), Tokens/sec, p50/p95/p99 latency, and concurrency (1, 5, 10 workers).
- **Quality Gates (`ml/inference/validate_quantized_quality.py`)**:
  - 100% regression validation across pricing, EMI, Hindi, Gujarati, and English comparisons.

### 5. 🧠 Production-Grade Hybrid RAG Engine
- **Dual Vector & Relational Store**:
  - `vehicle_record`: Structured SQL constraints + normalized vehicle vector embeddings.
  - `knowledge_chunk`: Unstructured knowledge chunks (brochures, manuals, EV charging guides, BH series RTO tax policies, B-NCAP crash standards).
- **Universal Multi-Format Ingestion**:
  - Supports `.pdf`, `.txt`, `.md`, `.html`, `.csv`, `.json`, and `.jsonl`.
  - Recursive semantic chunking (`chunk_size=500`, `chunk_overlap=50`) with SHA-256 deduplication.
  - CLI: `python scripts/ingest_knowledge_docs.py -p /path/to/docs --source "OEM Manuals"`
- **Reciprocal Rank Fusion (RRF) & Citation Grounding**:
  - Combines SQL candidate filtering, vector search, curated dataset records, and live DuckDuckGo web grounding.
  - Explicit evidence IDs (`[VEH-N]`, `[DOC-N]`, `[WEB-N]`) and strict grounding instructions preventing hallucinations.

---

## 🚀 Tech Stack

### Frontend
- **Framework**: React 18, Vite, TypeScript, TSX
- **Styling**: Tailwind CSS (Dark theme variables, glassmorphic panels, keyframe glows)
- **State & Router**: React Router v6, React Context
- **Animation**: Framer Motion
- **Markdown & Icons**: `react-markdown`, `remark-gfm`, Lucide React

### Backend
- **Core Framework**: Python 3.11+, FastAPI, Pydantic v2
- **Database ORM**: SQLAlchemy 2.0, Alembic, PyMySQL
- **Authentication**: JWT access tokens, Bcrypt password hashing
- **Streaming**: SSE-Starlette

### AI / ML & RAG Layer
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`), 384 dimensions
- **Vector Store**: `LocalFAISSVectorStore` (FAISS IndexFlatIP + NumPy cosine fallback)
- **Hybrid Retriever**: `HybridRetriever` (SQL Constraints + RRF Reranker + DDG Web Grounding)
- **LLM Providers**: `LocalAutoMindProvider` (default curated local engine), `QwenLocalProvider` (fine-tuned Qwen LoRA weights), `ConfigurableAPIProvider` (OpenAI/vLLM/Ollama)
- **Query Parser**: `QueryAnalyzer` (extracts budget, seats, airbags, body type, fuel type, Indic numerals, Hindi/Gujarati)

### Database
- **Primary Database**: MySQL 8.0

---

## 📂 Project Architecture

```text
c:\Project-V\
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Fast API versioned routes (auth, cars, chat, saved, admin, health)
│   │   ├── core/            # Config, security, JWT helpers
│   │   ├── db/              # SQLAlchemy session & base
│   │   ├── models/          # User, Source, CarModel, CarVariant, SavedCar, Conversation, Message, IngestionJob
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── repositories/    # User, Car, Chat, Ingestion repos
│   │   └── services/
│   │       ├── ai/          # VectorStore, EmbeddingService, QueryAnalyzer, HybridRetriever, LLMProvider
│   │       └── ingestion/   # DataLoader, DataValidator, DataNormalizer, IngestionPipeline
│   ├── scripts/             # seed_db.py, generate_car_data.py, import_csv.py, import_jsonl.py, build_embeddings.py
│   ├── tests/               # pytest test suite
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios client & endpoints
│   │   ├── components/      # UI, AI progress, Source cards, Car cards, Sidebar, Navbar
│   │   ├── context/         # AuthContext
│   │   ├── pages/           # Landing, Login, Register, Dashboard, Chat, CarDetail, Compare, Saved, Admin, Settings
│   │   ├── routes/          # AppRoutes
│   │   └── types/           # TypeScript interfaces
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── ml/                      # Optional fine-tuning datasets and training scripts
├── docker/                  # Dockerfile.backend, Dockerfile.frontend
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- MySQL 8.0 server (or Docker)

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# Seed realistic vehicles, sources, and demo user (demo@automind.ai / password123)
python scripts/seed_db.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
*Swagger API Documentation will be available at `http://localhost:8000/docs`.*

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend dev server will be live at `http://localhost:5173`.*

---

## 📊 Million-Record Benchmark & Data Ingestion

To test ingestion scalability for 10,000 or 1,000,000 car records:

```bash
# Generate and ingest 10,000 synthetic vehicle records into MySQL & Vector Store
python backend/scripts/generate_car_data.py --rows 10000

# Import external CSV dataset
python backend/scripts/import_csv.py --file data/sample_cars.csv --source "Kaggle Auto 2026"

# Re-build vector embeddings index
python backend/scripts/build_embeddings.py
```

---

## 🐳 Docker Deployment

To launch the full stack (MySQL 8 + FastAPI + React Frontend) using Docker Compose:

```bash
docker-compose up --build
```

---

## 🧪 Running Automated Tests

```bash
pytest backend/tests
```

---

## 🛡️ License & Security
Built with secure JWT token authentication, Bcrypt password hashing, and parameterized SQL queries. Grounded in structured automotive truth.
