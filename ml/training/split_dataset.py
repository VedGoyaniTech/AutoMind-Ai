"""
AutoMind AI — Production Dataset Splitter (Point 2 of Roadmap)
Splits dataset into:
  - 90% Training Set: train.jsonl
  - 10% Validation Set: validation.jsonl
  - Test Benchmark Evaluation Set: test_eval.jsonl
"""

import os
import sys
import json
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

SOURCE_DATASET = os.path.join(BASE_DIR, "ml", "datasets", "formatted_instruction_dataset.jsonl")
COMBINED_DATASET = os.path.join(BASE_DIR, "ml", "datasets", "combined_cleaned_dataset.jsonl")
DATASET_DIR = os.path.join(BASE_DIR, "ml", "datasets")

def create_formatted_instruction_dataset():
    """Build formatted_instruction_dataset.jsonl from combined_cleaned_dataset.jsonl."""
    if not os.path.exists(COMBINED_DATASET):
        print(f"[-] Combined dataset not found at {COMBINED_DATASET}.")
        return

    formatted_instructions = []
    with open(COMBINED_DATASET, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                if "instruction" in item and "output" in item:
                    prompt = item["instruction"]
                    response = item["output"]
                else:
                    prompt = item.get("query") or item.get("instruction") or item.get("text") or "Analyze entry."
                    response = item.get("passage") or item.get("context") or item.get("sentence") or item.get("text") or ""

                formatted_instructions.append({
                    "instruction": prompt.strip(),
                    "input": "",
                    "output": response.strip()
                })

    with open(SOURCE_DATASET, "w", encoding="utf-8") as f:
        for entry in formatted_instructions:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"[✔] Formatted {len(formatted_instructions)} instruction records -> {os.path.basename(SOURCE_DATASET)}")

def split_dataset(train_ratio: float = 0.9, seed: int = 42):
    if not os.path.exists(SOURCE_DATASET):
        print(f"[-] Source dataset not found at {SOURCE_DATASET}. Formatting dataset...")
        create_formatted_instruction_dataset()

    records = []
    if os.path.exists(SOURCE_DATASET):
        with open(SOURCE_DATASET, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    if not records:
        print("[-] No records found to split.")
        return

    print(f"[*] Total dataset records: {len(records)}")

    # Shuffle deterministically
    random.seed(seed)
    random.shuffle(records)

    split_idx = max(1, int(len(records) * train_ratio))
    train_set = records[:split_idx]
    val_set = records[split_idx:] if len(records) > 1 else records

    train_path = os.path.join(DATASET_DIR, "train.jsonl")
    val_path = os.path.join(DATASET_DIR, "validation.jsonl")
    eval_path = os.path.join(DATASET_DIR, "test_eval.jsonl")

    # Save train.jsonl
    with open(train_path, "w", encoding="utf-8") as f:
        for item in train_set:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Save validation.jsonl
    with open(val_path, "w", encoding="utf-8") as f:
        for item in val_set:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Save test_eval.jsonl
    with open(eval_path, "w", encoding="utf-8") as f:
        for item in val_set:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("\n[✔] DATASET SPLIT COMPLETED:")
    print(f"    - Training Set ({int(train_ratio*100)}%): {len(train_set)} records -> {os.path.basename(train_path)}")
    print(f"    - Validation Set: {len(val_set)} records -> {os.path.basename(val_path)}")
    print(f"    - Benchmark Test Set: {len(val_set)} records -> {os.path.basename(eval_path)}")

if __name__ == "__main__":
    split_dataset()
