"""
AutoMind AI — Advanced Hugging Face Dataset Cleaner & Training Pipeline
Features:
1. Best HF Dataset Loader & Integration
2. Fake / Junk Data Detection & Removal (Placeholders, empty text, short text, invalid/corrupted JSON)
3. Content Hashing & Exact Deduplication
4. Formats data for RAG Vector Index + LLM Fine-Tuning (Instruction JSONL)
5. 90/10 Train/Validation Split
6. Updates FAISS Vector Index
"""

import os
import sys
import json
import hashlib
import re
from typing import List, Dict, Any, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASETS_DIR = os.path.join(BASE_DIR, "ml", "datasets")
TRAINING_DIR = os.path.join(BASE_DIR, "ml", "training")

# Add paths to sys.path
sys.path.append(os.path.join(BASE_DIR, "backend"))
sys.path.append(TRAINING_DIR)

# Fake / Junk patterns to filter out
JUNK_PATTERNS = [
    r"^test$", r"^dummy$", r"^sample$", r"^n/a$", r"^nan$", r"^undefined$", r"^null$",
    r"\[insert\s+.*?\]", r"lorem\s+ipsum", r"asdf", r"qwerty", r"12345"
]

def is_fake_or_junk(row: Dict[str, Any]) -> Tuple[bool, str]:
    """Identify if a row contains fake, placeholder, corrupted, or junk data."""
    text_content = ""
    for k in ["text", "passage", "output", "query", "instruction", "content", "description"]:
        val = row.get(k)
        if isinstance(val, str) and val.strip():
            text_content += " " + val.strip()

    text_content = text_content.strip()

    # 1. Empty or extremely short content
    if not text_content or len(text_content) < 15:
        return True, "Too short or empty content (<15 chars)"

    # 2. Check junk/placeholder regex patterns
    lowered = text_content.lower()
    for pattern in JUNK_PATTERNS:
        if re.search(pattern, lowered):
            return True, f"Matched placeholder pattern: '{pattern}'"

    # 3. Check invalid characters or corrupted text ratio
    alpha_chars = sum(1 for c in text_content if c.isalnum() or c.isspace())
    if len(text_content) > 0 and (alpha_chars / len(text_content)) < 0.6:
        return True, "High ratio of corrupted / non-alphanumeric characters"

    return False, ""

def compute_content_hash(row: Dict[str, Any]) -> str:
    """Compute deterministic MD5 hash for exact deduplication."""
    filtered_keys = {k: v for k, v in row.items() if k not in ['id', '_id', 'index', '_source_dataset']}
    serialized = json.dumps(filtered_keys, sort_keys=True)
    return hashlib.md5(serialized.encode('utf-8')).hexdigest()

def clean_and_process_dataset():
    print("=" * 70)
    print(" AUTOMIND AI — HUGGING FACE DATASET CLEANER & TRAINING PIPELINE ")
    print("=" * 70)

    combined_input_path = os.path.join(DATASETS_DIR, "combined_cleaned_dataset.jsonl")
    if not os.path.exists(combined_input_path):
        print(f"[-] Input file not found: {combined_input_path}")
        return

    raw_rows = []
    with open(combined_input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    raw_rows.append(json.loads(line))
                except Exception:
                    pass

    total_raw = len(raw_rows)
    print(f"[*] Loaded {total_raw} raw dataset records.")

    # 1. Clean fake / junk data
    valid_rows = []
    fake_count = 0
    fake_reasons = {}

    for row in raw_rows:
        is_junk, reason = is_fake_or_junk(row)
        if is_junk:
            fake_count += 1
            fake_reasons[reason] = fake_reasons.get(reason, 0) + 1
        else:
            valid_rows.append(row)

    print(f"[✔] Removed {fake_count} fake/corrupted/junk records.")
    for reason, count in fake_reasons.items():
        print(f"    - Filtered ({count}): {reason}")

    # 2. Deduplicate records
    seen_hashes = set()
    deduped_rows = []
    dup_count = 0

    for row in valid_rows:
        h = compute_content_hash(row)
        if h in seen_hashes:
            dup_count += 1
        else:
            seen_hashes.add(h)
            deduped_rows.append(row)

    print(f"[✔] Removed {dup_count} duplicate records.")
    print(f"[★] Total High-Quality Clean Records: {len(deduped_rows)} (from {total_raw} raw)")

    # 3. Save cleaned master dataset
    master_cleaned_file = os.path.join(DATASETS_DIR, "combined_cleaned_dataset.jsonl")
    with open(master_cleaned_file, "w", encoding="utf-8") as f:
        for item in deduped_rows:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # 4. Generate Instruction Dataset (train.jsonl and validation.jsonl)
    instruction_rows = []
    for item in deduped_rows:
        src = item.get("_source_dataset", "HuggingFace Dataset")
        instr = item.get("instruction") or item.get("query") or f"Describe vehicle knowledge from [{src}]"
        inp = item.get("input", "")
        out = item.get("output") or item.get("passage") or item.get("text") or item.get("context") or ""
        
        if instr and out:
            instruction_rows.append({
                "instruction": f"[{src}] {instr}",
                "input": inp,
                "output": out
            })

    # Save formatted instruction dataset
    formatted_file = os.path.join(DATASETS_DIR, "formatted_instruction_dataset.jsonl")
    with open(formatted_file, "w", encoding="utf-8") as f:
        for item in instruction_rows:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # 5. Split into 90% Train / 10% Validation
    train_count = int(len(instruction_rows) * 0.9)
    train_data = instruction_rows[:train_count]
    val_data = instruction_rows[train_count:]

    train_path = os.path.join(DATASETS_DIR, "train.jsonl")
    val_path = os.path.join(DATASETS_DIR, "validation.jsonl")

    with open(train_path, "w", encoding="utf-8") as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(val_path, "w", encoding="utf-8") as f:
        for item in val_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[✔] Saved Train Dataset: {len(train_data)} rows -> ml/datasets/train.jsonl")
    print(f"[✔] Saved Validation Dataset: {len(val_data)} rows -> ml/datasets/validation.jsonl")

    # 6. Run Vector Ingestion
    print("\n[*] Triggering Vector Index Ingestion with Cleaned Dataset...")
    try:
        from ingest_to_vector_index import ingest_dataset
        ingest_dataset()
    except Exception as e:
        print(f"[-] Vector ingestion error: {e}")

    print("\n" + "=" * 70)
    print(" DATASET CLEANING & TRAINING PREPARATION PIPELINE COMPLETE ")
    print("=" * 70)

if __name__ == "__main__":
    clean_and_process_dataset()
