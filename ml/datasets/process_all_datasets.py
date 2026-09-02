import json
import os
import hashlib
import urllib.request
from typing import List, Dict, Any, Tuple

DATASET_LIST = [
    "darkB/electric-vehicles-qa-dataset"
]

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_row_content_hash(row: Dict[str, Any]) -> str:
    """Generate MD5 hash of row content for deduplication."""
    content_str = json.dumps({k: v for k, v in row.items() if k not in ['id', '_id', 'index']}, sort_keys=True)
    return hashlib.md5(content_str.encode('utf-8')).hexdigest()

def fetch_hf_dataset_rows(dataset_name: str, max_rows: int = 5000) -> List[Dict[str, Any]]:
    """Fetch rows for a dataset using Hugging Face datasets-server API with pagination (max 100 per request)."""
    print(f"\n[*] Fetching records for dataset: {dataset_name}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    rows = []
    offset = 0
    limit = 100
    
    # First, try to detect the config and split
    cfg = "default"
    splt = "train"
    try:
        config_url = f"https://datasets-server.huggingface.co/splits?dataset={dataset_name}"
        config_req = urllib.request.Request(config_url, headers=headers)
        with urllib.request.urlopen(config_req, timeout=30) as c_resp:
            c_payload = json.loads(c_resp.read().decode('utf-8'))
            splits = c_payload.get('splits', [])
            if splits:
                cfg = splits[0].get('config', 'default')
                splt = splits[0].get('split', 'train')
    except Exception as err:
        print(f"    [-] Could not fetch splits info ({err}). Defaulting to default/train.")

    while len(rows) < max_rows:
        chunk_size = min(limit, max_rows - len(rows))
        url = f"https://datasets-server.huggingface.co/rows?dataset={dataset_name}&config={cfg}&split={splt}&offset={offset}&length={chunk_size}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                payload = json.loads(response.read().decode('utf-8'))
                raw_rows = payload.get('rows', [])
                if not raw_rows:
                    break
                chunk_rows = [item.get('row', {}) for item in raw_rows if 'row' in item]
                rows.extend(chunk_rows)
                print(f"    [+] Fetched {len(chunk_rows)} rows (offset: {offset})")
                if len(chunk_rows) < chunk_size:
                    # No more rows available
                    break
                offset += len(chunk_rows)
        except Exception as err:
            print(f"    [-] Error fetching offset {offset}: {err}")
            break
            
    print(f"    [+] Successfully fetched {len(rows)} total rows from Datasets Server.")
    return rows

def parse_row(dataset_name: str, r: Dict[str, Any]) -> Dict[str, Any]:
    """Parse dataset-specific row schema into standardized instruction-following schema."""
    if dataset_name == "darkB/electric-vehicles-qa-dataset":
        text = r.get("text", "")
        if "[INST]" in text and "[/INST]" in text:
            parts = text.replace("<s>", "").replace("</s>", "").split("[/INST]")
            question = parts[0].replace("[INST]", "").strip()
            answer = parts[1].strip()
            return {
                "instruction": question,
                "input": "",
                "output": answer,
                "_source_dataset": dataset_name
            }
    return r

def process_and_convert_dataset(dataset_name: str) -> Tuple[str, int, int]:
    """Download, deduplicate, and convert dataset to JSONL."""
    rows = fetch_hf_dataset_rows(dataset_name)
    
    if not rows:
        print(f"    [!] No rows retrieved for {dataset_name}.")
        return "", 0, 0

    total_count = len(rows)
    seen_hashes = set()
    deduped_rows = []

    for r in rows:
        parsed = parse_row(dataset_name, r)
        if parsed:
            h = get_row_content_hash(parsed)
            if h not in seen_hashes:
                seen_hashes.add(h)
                deduped_rows.append(parsed)

    dedup_count = len(deduped_rows)
    duplicates_removed = total_count - dedup_count

    safe_name = dataset_name.replace("/", "_").replace("-", "_") + ".jsonl"
    out_file = os.path.join(OUTPUT_DIR, safe_name)

    with open(out_file, "w", encoding="utf-8") as f:
        for item in deduped_rows:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"    [✔] Saved {dedup_count} parsed & deduplicated rows to: {safe_name} (Removed {duplicates_removed} duplicates)")
    return out_file, total_count, dedup_count

def main():
    print("=" * 70)
    print(" HUGGING FACE DATASET CONVERTER & DEDUPLICATOR ")
    print("=" * 70)

    results = []
    combined_rows = []

    # Clean old fake dataset files from the filesystem
    old_files = [
        "Carlisle_msmacro-test-corpus.jsonl",
        "Carlisle_msmacro_test_corpus.jsonl",
        "CarperAI_pilev2_dev.jsonl",
        "carbon225_poleval-abbreviation-disambiguation-wiki.jsonl",
        "carbon225_poleval_abbreviation_disambiguation_wiki.jsonl",
        "carolina_c4ai_corpus_carolina.jsonl",
        "carolmou_dataset-1.jsonl",
        "carolmou_dataset_1.jsonl",
        "carsondial_qwen_8b_embed.jsonl",
        "librarian_bots_model_card_sentences.jsonl"
    ]
    print("[*] Cleaning up old fake/placeholder dataset files...")
    for old_file in old_files:
        p = os.path.join(OUTPUT_DIR, old_file)
        if os.path.exists(p):
            os.remove(p)
            print(f"    - Removed old file: {old_file}")

    for ds in DATASET_LIST:
        filepath, raw_cnt, clean_cnt = process_and_convert_dataset(ds)
        if not filepath:
            continue
        results.append({
            "dataset": ds,
            "output_file": os.path.basename(filepath),
            "raw_records": raw_cnt,
            "deduplicated_records": clean_cnt,
            "duplicates_removed": raw_cnt - clean_cnt
        })

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        combined_rows.append(item)

    # Deduplicate combined master dataset
    combined_file = os.path.join(OUTPUT_DIR, "combined_cleaned_dataset.jsonl")
    seen_hashes = set()
    master_clean = []
    for item in combined_rows:
        h = get_row_content_hash(item)
        if h not in seen_hashes:
            seen_hashes.add(h)
            master_clean.append(item)

    with open(combined_file, "w", encoding="utf-8") as f:
        for item in master_clean:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("\n" + "=" * 70)
    print(f" COMBINED MASTER DATASET SAVED: combined_cleaned_dataset.jsonl ({len(master_clean)} records)")
    print("=" * 70)

    # Print Summary Table
    print("\nSUMMARY REPORT:")
    print("-" * 70)
    print(f"{'Dataset Name':<50} | {'Clean Rows':<10}")
    print("-" * 70)
    for r in results:
        print(f"{r['dataset']:<50} | {r['deduplicated_records']:<10}")
    print("-" * 70)

if __name__ == "__main__":
    main()

