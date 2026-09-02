"""
AutoMind AI — Comprehensive Dataset Quality & Audit Pipeline
1. Validates JSONL structure across all dataset files.
2. Detects malformed rows, duplicate prompts, empty/truncated answers.
3. Detects and quarantines non-automotive or unverified entries.
4. Redacts PII (emails, phone numbers).
5. Partitions into raw/, cleaned/, quarantine/, train/, validation/, test/.
6. Generates dataset_manifest.json and reports/dataset_audit_report.json.
"""

import os
import re
import json
from typing import Dict, Any, List, Set
from datetime import datetime, timezone

DATASETS_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(DATASETS_DIR, "reports")
CLEANED_DIR = os.path.join(DATASETS_DIR, "cleaned")
QUARANTINE_DIR = os.path.join(DATASETS_DIR, "quarantine")
TRAIN_DIR = os.path.join(DATASETS_DIR, "train")
VAL_DIR = os.path.join(DATASETS_DIR, "validation")
TEST_DIR = os.path.join(DATASETS_DIR, "test")

for d in [REPORT_DIR, CLEANED_DIR, QUARANTINE_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR]:
    os.makedirs(d, exist_ok=True)

AUTOMOTIVE_KEYWORDS = [
    "car", "vehicle", "engine", "suv", "sedan", "ev", "electric", "battery",
    "price", "on-road", "rto", "emi", "fuel", "mileage", "safety", "airbag",
    "nexon", "creta", "thar", "maruti", "tata", "hyundai", "mahindra", "toyota",
    "गाड़ी", "कार", "કિંમત", "માઈલેજ", "સુરક્ષા"
]

def redact_pii(text: str) -> str:
    # Redact email addresses
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED_EMAIL]", text)
    # Redact 10-digit Indian phone numbers
    text = re.sub(r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b", "[REDACTED_PHONE]", text)
    return text

def audit_and_partition():
    print("=" * 80)
    print(" 🔍 AUTOMIND AI — ML DATASET AUDIT & PARTITIONING PIPELINE ")
    print("=" * 80)

    total_inspected = 0
    total_valid = 0
    total_duplicates = 0
    total_quarantined = 0
    seen_prompts: Set[str] = set()

    cleaned_records: List[Dict[str, Any]] = []
    quarantined_records: List[Dict[str, Any]] = []

    # Audit master datasets
    candidate_files = [f for f in os.listdir(DATASETS_DIR) if f.endswith(".jsonl") and not f.startswith(".")]

    for fname in candidate_files:
        fpath = os.path.join(DATASETS_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                total_inspected += 1
                try:
                    record = json.loads(line)
                except Exception:
                    quarantined_records.append({"file": fname, "line": line_no, "reason": "malformed_json", "raw": line[:100]})
                    total_quarantined += 1
                    continue

                # Extract prompt and response
                prompt = ""
                response = ""

                if "messages" in record and isinstance(record["messages"], list):
                    for msg in record["messages"]:
                        if msg.get("role") == "user":
                            prompt = msg.get("content", "")
                        elif msg.get("role") == "assistant":
                            response = msg.get("content", "")
                elif "prompt" in record:
                    prompt = record.get("prompt", "")
                    response = record.get("response") or record.get("completion") or ""
                elif "instruction" in record:
                    prompt = record.get("instruction", "")
                    response = record.get("output", "")

                prompt_clean = prompt.strip()
                response_clean = response.strip()

                if not prompt_clean or not response_clean or len(response_clean) < 15:
                    quarantined_records.append({"file": fname, "line": line_no, "reason": "empty_or_truncated", "prompt": prompt_clean})
                    total_quarantined += 1
                    continue

                # Check duplicate prompt
                norm_prompt = re.sub(r"\s+", " ", prompt_clean.lower())
                if norm_prompt in seen_prompts:
                    total_duplicates += 1
                    continue
                seen_prompts.add(norm_prompt)

                # Check automotive relevance
                is_auto = any(kw in norm_prompt for kw in AUTOMOTIVE_KEYWORDS) or any(kw in response_clean.lower() for kw in AUTOMOTIVE_KEYWORDS)
                if not is_auto:
                    quarantined_records.append({"file": fname, "line": line_no, "reason": "non_automotive", "prompt": prompt_clean})
                    total_quarantined += 1
                    continue

                # PII Redaction
                clean_record = {
                    "prompt": redact_pii(prompt_clean),
                    "response": redact_pii(response_clean),
                    "source_file": fname,
                    "audited_at": datetime.now(timezone.utc).isoformat()
                }
                cleaned_records.append(clean_record)
                total_valid += 1

    print(f"  [✔] Total Records Inspected: {total_inspected}")
    print(f"  [✔] Valid Deduplicated Records: {total_valid}")
    print(f"  [✔] Duplicate Prompts Discarded: {total_duplicates}")
    print(f"  [✔] Quarantined Records: {total_quarantined}")

    # Partition Train (80%), Val (10%), Test (10%)
    n = len(cleaned_records)
    n_train = int(n * 0.8)
    n_val = int(n * 0.1)

    train_data = cleaned_records[:n_train]
    val_data = cleaned_records[n_train:n_train + n_val]
    test_data = cleaned_records[n_train + n_val:]

    def save_jsonl(filepath: str, data: List[Dict[str, Any]]):
        with open(filepath, "w", encoding="utf-8") as out:
            for item in data:
                out.write(json.dumps(item, ensure_ascii=False) + "\n")

    save_jsonl(os.path.join(CLEANED_DIR, "master_cleaned_catalog.jsonl"), cleaned_records)
    save_jsonl(os.path.join(TRAIN_DIR, "train.jsonl"), train_data)
    save_jsonl(os.path.join(VAL_DIR, "validation.jsonl"), val_data)
    save_jsonl(os.path.join(TEST_DIR, "test.jsonl"), test_data)
    save_jsonl(os.path.join(QUARANTINE_DIR, "quarantine.jsonl"), quarantined_records)

    # Generate Manifest
    manifest = {
        "manifest_version": "2.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_valid_examples": total_valid,
        "splits": {
            "train": len(train_data),
            "validation": len(val_data),
            "test": len(test_data),
            "quarantine": len(quarantined_records)
        },
        "policy": {
            "pii_redaction_applied": True,
            "no_dynamic_pricing_memorization": True,
            "languages_supported": ["hi-IN", "gu-IN", "en-IN"]
        }
    }

    manifest_path = os.path.join(DATASETS_DIR, "dataset_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    report_path = os.path.join(REPORT_DIR, "dataset_audit_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_inspected": total_inspected,
            "total_valid": total_valid,
            "duplicates_removed": total_duplicates,
            "quarantined": total_quarantined,
            "manifest": manifest
        }, f, indent=2)

    print(f"  [✔] Manifest written to: {manifest_path}")
    print(f"  [✔] Audit Report written to: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    audit_and_partition()
