import sys
import os
import argparse
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.services.ingestion.pipeline import IngestionPipeline
from app.core.config import settings

def import_csv(file_path: str, source_name: str = "CSV Importer"):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    print(f"Importing CSV dataset from {file_path}...")
    records = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    db = SessionLocal()
    vector_store = LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
    pipeline = IngestionPipeline(db, vector_store)

    job = pipeline.process_records(source_name=source_name, records=records)
    print(f"CSV Ingestion complete! Processed: {job.processed_records}, Failed: {job.failed_records}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSV Data Importer")
    parser.add_argument("--file", type=str, required=True, help="Path to CSV dataset")
    parser.add_argument("--source", type=str, default="CSV Importer", help="Source name metadata")
    args = parser.parse_args()

    import_csv(args.file, args.source)
