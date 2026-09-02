"""
AutoMind AI — Connect Combined Dataset to Vector Index
Ingests combined_cleaned_dataset.jsonl into the backend vector store
so the RAG pipeline retrieves from the full knowledge base.

Run from: c:\Project-V
Command:  $env:PYTHONPATH="c:\Project-V\backend"; .\.venv\Scripts\python.exe ml\ingest_dataset_to_vector.py
"""

import os
import sys
import json
import numpy as np

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

DATASET_PATH = os.path.join(BASE_DIR, "ml", "datasets", "combined_cleaned_dataset.jsonl")
VECTOR_INDEX_PATH = os.path.join(BASE_DIR, "backend", "vector_index")


def extract_text(record: dict) -> str:
    """Extract the main text content from any record format."""
    # Try common text fields in priority order
    for field in ["passage", "text", "content", "answer", "response"]:
        if field in record and record[field]:
            return str(record[field]).strip()

    # Fallback: combine query + instruction
    parts = []
    if "query" in record:
        parts.append(record["query"])
    if "instruction" in record:
        parts.append(record["instruction"])
    if parts:
        return " ".join(parts)

    return ""


def get_title(record: dict) -> str:
    """Extract a title/label for the record."""
    for field in ["title", "query", "instruction", "doc_id", "id"]:
        if field in record and record[field]:
            return str(record[field])[:80]
    return "Knowledge Record"


def ingest_dataset_to_vector_index():
    print("=" * 65)
    print(" AUTOMIND AI — CONNECTING DATASET TO VECTOR INDEX ")
    print("=" * 65)

    # Load dataset
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset not found: {DATASET_PATH}")
        return

    records = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    continue

    print(f"[✔] Loaded {len(records)} records from combined_cleaned_dataset.jsonl")

    # Filter records with meaningful text
    docs = []
    for r in records:
        text = extract_text(r)
        if len(text) > 20:  # Skip very short entries
            docs.append({
                "text": text,
                "title": get_title(r),
                "source": r.get("_source_dataset", r.get("source", "AutoMind Dataset")),
                "car_variant_id": None,  # Not a car variant, knowledge doc
                "url": r.get("url", ""),
                "score": r.get("score", 1.0),
            })

    print(f"[✔] Filtered to {len(docs)} valid knowledge documents")

    # Load embedding service
    from app.services.ai.embedding_service import embedding_service

    print(f"[*] Encoding {len(docs)} documents with sentence-transformers...")
    texts = [d["text"] for d in docs]
    embeddings = embedding_service.encode(texts)
    embeddings = np.array(embeddings, dtype="float32")
    print(f"[✔] Embeddings shape: {embeddings.shape}")

    # Load vector store and add documents
    from app.services.ai.vector_store import LocalFAISSVectorStore

    print(f"[*] Loading existing vector index from: {VECTOR_INDEX_PATH}")
    vs = LocalFAISSVectorStore(VECTOR_INDEX_PATH)
    existing_count = len(vs.documents)
    print(f"[*] Existing documents in index: {existing_count}")

    print(f"[*] Adding {len(docs)} new documents to vector index...")
    vs.add_documents(docs, embeddings)
    vs.save(VECTOR_INDEX_PATH)

    print(f"[✔] Vector index now contains: {len(vs.documents)} total documents")
    print(f"[✔] Saved to: {VECTOR_INDEX_PATH}")

    print("\n" + "=" * 65)
    print(f" DATASET CONNECTED SUCCESSFULLY — {len(docs)} docs ingested ")
    print("=" * 65)
    print(f"\n  Vector Index Path : {VECTOR_INDEX_PATH}")
    print(f"  Documents Added   : {len(docs)}")
    print(f"  Embedding Dim     : {embeddings.shape[1]}")
    print(f"  Total in Index    : {len(vs.documents)}")


if __name__ == "__main__":
    ingest_dataset_to_vector_index()
