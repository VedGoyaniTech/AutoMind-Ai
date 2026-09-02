import json
import urllib.request
import os

DATASETS = [
    "carsondial/qwen-8b-embed",
    "Carlisle/msmacro-test-corpus",
    "carolina-c4ai/corpus-carolina",
    "CarperAI/pilev2-dev",
    "carbon225/poleval-abbreviation-disambiguation-wiki",
    "carolmou/dataset-1",
    "librarian-bots/model-card-sentences",
    "tatsu-lab/alpaca",
    "garage-bAInd/Open-Platypus"
]

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def fetch_dataset_rows(dataset_id, max_rows=1000):
    print(f"[*] Fetching rows for Hugging Face Dataset: {dataset_id}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # 1. Discover available splits and configs
    splits_url = f"https://datasets-server.huggingface.co/splits?dataset={dataset_id}"
    req_splits = urllib.request.Request(splits_url, headers=headers)
    
    config_name = "default"
    split_name = "train"
    
    try:
        with urllib.request.urlopen(req_splits, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            splits = data.get('splits', [])
            if splits:
                config_name = splits[0].get('config', 'default')
                split_name = splits[0].get('split', 'train')
                print(f"    [+] Discovered split: config='{config_name}', split='{split_name}'")
    except Exception as e:
        print(f"    [-] Split discovery note: {e}")

    # 2. Fetch rows in chunks of 50
    rows = []
    chunk_size = 50
    for offset in range(0, max_rows, chunk_size):
        url = f"https://datasets-server.huggingface.co/rows?dataset={dataset_id}&config={config_name}&split={split_name}&offset={offset}&length={min(chunk_size, max_rows - offset)}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                fetched = [item['row'] for item in data.get('rows', []) if 'row' in item]
                if not fetched:
                    break
                rows.extend(fetched)
        except Exception as e:
            print(f"    [-] Chunk fetch at offset {offset} error: {e}")
            break
            
    if rows:
        print(f"    [✔] Successfully fetched {len(rows)} live HF rows for {dataset_id}")
        return rows
    else:
        return fetch_parquet_fallback(dataset_id)

def fetch_parquet_fallback(dataset_id):
    info_url = f"https://datasets-server.huggingface.co/parquet?dataset={dataset_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(info_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            files = data.get('parquet_files', [])
            print(f"Found {len(files)} parquet files for {dataset_id}")
            if files:
                first_url = files[0]['url']
                print(f"Sample Parquet URL: {first_url}")
    except Exception as e:
        print(f"Parquet info error for {dataset_id}: {e}")
    return []

def deduplicate_and_save(dataset_id, rows):
    filename = dataset_id.replace("/", "_") + ".jsonl"
    out_path = os.path.join(OUTPUT_DIR, filename)
    
    seen_hashes = set()
    unique_rows = []
    
    for r in rows:
        # Create hash representation of row dict
        serialized = json.dumps(r, sort_keys=True)
        if serialized not in seen_hashes:
            seen_hashes.add(serialized)
            unique_rows.append(r)
            
    print(f"Original count: {len(rows)} | Unique count: {len(unique_rows)} | Removed {len(rows) - len(unique_rows)} duplicates")
    
    with open(out_path, "w", encoding="utf-8") as f:
        for r in unique_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print(f"Saved: {out_path}")
    return out_path, len(unique_rows)

if __name__ == "__main__":
    summary = {}
    for ds_id in DATASETS:
        rows = fetch_dataset_rows(ds_id)
        if rows:
            out_p, count = deduplicate_and_save(ds_id, rows)
            summary[ds_id] = {"path": out_p, "count": count}
        else:
            summary[ds_id] = {"error": "Could not fetch rows automatically"}
            
    print("\n=== PROCESSING SUMMARY ===")
    print(json.dumps(summary, indent=2))
