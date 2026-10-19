"""
AutoMind AI — Connect Master Automotive Dataset to Vector Index & Fast RAG Store.
Ingests automind_car_master_dataset.json into the backend vector store
so the RAG pipeline retrieves from the verified knowledge base with high accuracy.
"""

import os
import sys
import json
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Inside container fallback
CONTAINER_APP = "/app"
if os.path.exists(CONTAINER_APP) and CONTAINER_APP not in sys.path:
    sys.path.insert(0, CONTAINER_APP)

DATASET_JSON_PATH = os.path.join(BASE_DIR, "ml", "datasets", "automind_car_master_dataset.json")
VECTOR_INDEX_PATHS = [
    os.path.join(BASE_DIR, "backend", "vector_index"),
    "/app/vector_index"
]


def ingest_master_dataset():
    print("=" * 70)
    print(" 🚗 AUTOMIND AI — INGESTING MASTER DATASET INTO VECTOR STORE ")
    print("=" * 70)

    if not os.path.exists(DATASET_JSON_PATH):
        print(f"[ERROR] Master dataset not found at: {DATASET_JSON_PATH}")
        return

    with open(DATASET_JSON_PATH, "r", encoding="utf-8") as f:
        master_records = json.load(f)

    print(f"[✔] Loaded {len(master_records)} records from automind_car_master_dataset.json")

    # Format into knowledge chunks for Hybrid Retriever
    docs_to_add = []
    for r in master_records:
        inst = r.get("instruction", "").strip()
        out = r.get("output", "").strip()
        if not inst or not out:
            continue
        c_id = r.get("id", f"chunk_{len(docs_to_add) + 1}")
        full_text = f"User Question: {inst}\nVerified Answer & Automotive Facts:\n{out}"
        docs_to_add.append({
            "doc_type": "knowledge_chunk",
            "chunk_id": c_id,
            "title": inst,
            "text": full_text,
            "category": r.get("category", "automotive_spec"),
            "metadata": r.get("metadata", {}),
            "source_name": "AutoMind Master Automotive Database",
            "source_url": "https://automind.ai/knowledge",
            "date": "2024-2026",
            "car_variant_id": None
        })

    print(f"[✔] Prepared {len(docs_to_add)} formatted knowledge chunks.")

    from app.services.ai.embedding_service import embedding_service
    from app.services.ai.vector_store import LocalFAISSVectorStore

    print(f"[*] Computing vector embeddings for {len(docs_to_add)} knowledge chunks...")
    texts = [d["text"] for d in docs_to_add]
    embeddings = embedding_service.encode(texts)
    embeddings = np.array(embeddings, dtype="float32")
    print(f"[✔] Computed embeddings matrix: {embeddings.shape}")

    # Update all available vector index locations (host and docker container)
    for v_path in VECTOR_INDEX_PATHS:
        if not os.path.exists(v_path):
            try:
                os.makedirs(v_path, exist_ok=True)
            except Exception:
                continue

        print(f"[*] Updating Vector Index at: {v_path}")
        vs = LocalFAISSVectorStore(v_path)
        existing_count = len(vs.documents)
        print(f"    Current documents in store: {existing_count}")

        # Filter out existing chunk_ids to avoid duplicates
        existing_chunks = {d.get("chunk_id") for d in vs.documents if d.get("chunk_id")}
        new_docs = []
        new_indices = []
        for i, d in enumerate(docs_to_add):
            if d["chunk_id"] not in existing_chunks:
                new_docs.append(d)
                new_indices.append(i)

        if new_docs:
            print(f"    Adding {len(new_docs)} new knowledge chunks (filtered {len(docs_to_add) - len(new_docs)} existing)...")
            sub_embeddings = embeddings[new_indices]
            vs.add_documents(new_docs, sub_embeddings)
            vs.save(v_path)
            print(f"    [✔] Successfully updated {v_path} -> Total documents: {len(vs.documents)}")
        else:
            print(f"    [✔] Index at {v_path} is already up to date with all master chunks.")

    print("\n" + "=" * 70)
    print(" 🎉 MASTER DATASET SUCCESSFULLY INGESTED & CONNECTED TO RAG ")
    print("=" * 70)


if __name__ == "__main__":
    ingest_master_dataset()
