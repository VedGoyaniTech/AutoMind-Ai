import sys
import os
import argparse
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.services.ingestion.pipeline import IngestionPipeline
from app.core.config import settings

def import_jsonl(file_path: str, source_name: str = "JSONL Importer"):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    print(f"Importing JSONL dataset from {file_path}...")
    records = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    db = SessionLocal()
    vector_store = LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
    pipeline = IngestionPipeline(db, vector_store)

    job = pipeline.process_records(source_name=source_name, records=records)
    print(f"JSONL Ingestion complete! Processed: {job.processed_records}, Failed: {job.failed_records}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSONL Data Importer")
    parser.add_argument("--file", type=str, required=True, help="Path to JSONL dataset")
    parser.add_argument("--source", type=str, default="JSONL Importer", help="Source name metadata")
    args = parser.parse_args()

    import_jsonl(args.file, args.source)
