import os
import sys
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ingestion.document_pipeline import DocumentIngestionPipeline
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.core.config import settings

def main():
    parser = argparse.ArgumentParser(description="AutoMind AI Knowledge Document Ingestion Utility")
    parser.add_argument("--path", "-p", required=True, help="Path to file or directory of documents (.pdf, .txt, .md, .html, .csv, .json, .jsonl)")
    parser.add_argument("--source", "-s", default="Automotive Knowledge", help="Source name for citations")
    parser.add_argument("--reindex", "-r", action="store_true", help="Force re-indexing and overwrite existing chunks")
    args = parser.parse_args()

    target_path = os.path.abspath(args.path)
    if not os.path.exists(target_path):
        print(f"Error: Path does not exist: {target_path}")
        sys.exit(1)

    print("=" * 70)
    print(f"🚀 AutoMind AI Document Ingestion Pipeline")
    print(f"Target: {target_path}")
    print(f"Source: {args.source}")
    print(f"Vector Store Path: {settings.VECTOR_INDEX_PATH}")
    print(f"Re-index: {args.reindex}")
    print("=" * 70)

    store = LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
    pipeline = DocumentIngestionPipeline(store)

    if os.path.isfile(target_path):
        res = pipeline.ingest_file(target_path, source_name=args.source, reindex=args.reindex)
        print(f"\n[Result] File: {res['file_path']}")
        print(f"Total Chunks: {res['total_chunks']} | Indexed: {res['indexed_chunks']} | Skipped Duplicates: {res['skipped_duplicates']}")
    else:
        res = pipeline.ingest_directory(target_path, source_name=args.source, reindex=args.reindex)
        print(f"\n[Result] Directory: {res['directory']}")
        print(f"Files Processed: {res['files_processed']}")
        print(f"Total Chunks Indexed: {res['total_indexed_chunks']} | Total Skipped Duplicates: {res['total_skipped_duplicates']}")

    print("\n✔ Ingestion finished successfully!")

if __name__ == "__main__":
    main()
