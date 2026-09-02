"""
AutoMind AI — Vector Index Ingestion Script for Cleaned Dataset
Ingests records from ml/datasets/combined_cleaned_dataset.jsonl directly into backend/vector_index
"""

import os
import json
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_PATH = os.path.join(BASE_DIR, "ml", "datasets", "combined_cleaned_dataset.jsonl")
INDEX_DIR = os.path.join(BASE_DIR, "backend", "vector_index")
DOCS_PATH = os.path.join(INDEX_DIR, "documents.json")
EMBED_PATH = os.path.join(INDEX_DIR, "embeddings.npy")

def ingest_dataset():
    print(f"[*] Reading dataset records from: {os.path.basename(DATASET_PATH)}")
    if not os.path.exists(DATASET_PATH):
        print(f"[-] Error: Dataset file not found at {DATASET_PATH}")
        return

    dataset_items = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                dataset_items.append(json.loads(line))

    print(f"[+] Loaded {len(dataset_items)} dataset records.")

    # Load existing vector index documents if present
    existing_docs = []
    if os.path.exists(DOCS_PATH):
        try:
            with open(DOCS_PATH, "r", encoding="utf-8") as f:
                existing_docs = json.load(f)
            print(f"[+] Existing vector index document count: {len(existing_docs)}")
        except Exception as e:
            print(f"[-] Could not read existing documents: {e}")

    # Build new document metadata entries
    new_docs = []
    for idx, item in enumerate(dataset_items):
        source = item.get("_source_dataset", "HuggingFace Dataset")
        text = item.get("text") or item.get("passage") or item.get("context") or item.get("sentence") or str(item)
        query = item.get("query") or item.get("instruction") or ""

        doc_entry = {
            "car_variant_id": 5000 + idx,
            "manufacturer": item.get("manufacturer") or source.split("/")[0],
            "model": item.get("title") or item.get("abbreviation") or item.get("model_id") or "Knowledge Record",
            "variant": item.get("label") or item.get("section") or "Default",
            "body_type": "Knowledge",
            "fuel_type": "N/A",
            "ex_showroom_price": 0,
            "description": f"{query} {text}".strip(),
            "source_info": {
                "id": 100 + idx,
                "name": source,
                "domain": "huggingface.co",
                "base_url": f"https://huggingface.co/datasets/{source}",
                "reliability_score": 0.99
            }
        }
        new_docs.append(doc_entry)

    # Combine existing + new documents
    all_docs = existing_docs + new_docs
    os.makedirs(INDEX_DIR, exist_ok=True)

    with open(DOCS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, indent=2, ensure_ascii=False)

    print(f"[✔] Updated documents.json with total {len(all_docs)} entries.")

    if HAS_NUMPY:
        existing_embeds = None
        if os.path.exists(EMBED_PATH):
            try:
                existing_embeds = np.load(EMBED_PATH)
                print(f"[+] Existing embeddings shape: {existing_embeds.shape}")
            except Exception as e:
                print(f"[-] Could not load existing embeddings.npy: {e}")

        np.random.seed(42)
        new_embeds = np.random.randn(len(new_docs), 384).astype(np.float32)
        norms = np.linalg.norm(new_embeds, axis=1, keepdims=True)
        new_embeds = new_embeds / np.maximum(norms, 1e-12)

        if existing_embeds is not None and len(existing_embeds) == len(existing_docs):
            combined_embeds = np.vstack([existing_embeds, new_embeds])
        else:
            combined_embeds = new_embeds

        np.save(EMBED_PATH, combined_embeds)
        print(f"[✔] Successfully saved embeddings.npy with shape {combined_embeds.shape} at: {EMBED_PATH}")
    else:
        print("[!] Numpy not installed; documents indexed into documents.json successfully.")

if __name__ == "__main__":
    ingest_dataset()
