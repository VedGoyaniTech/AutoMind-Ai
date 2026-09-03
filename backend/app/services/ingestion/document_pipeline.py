import os
import hashlib
import logging
from typing import List, Dict, Any, Optional
from app.services.ingestion.document_parser import DocumentParser
from app.services.ingestion.chunker import RecursiveDocumentChunker
from app.services.ai.embedding_service import embedding_service
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.core.config import settings

logger = logging.getLogger(__name__)

class DocumentIngestionPipeline:
    """
    End-to-end ingestion pipeline for unstructured automotive knowledge documents:
    Brochures, owner manuals, policy updates, EV charging guides, and verified automotive articles.
    """

    def __init__(self, vector_store: Optional[LocalFAISSVectorStore] = None):
        self.vector_store = vector_store or LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
        self.chunker = RecursiveDocumentChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def ingest_file(
        self,
        file_path: str,
        source_name: str = "Automotive Knowledge",
        reindex: bool = False
    ) -> Dict[str, Any]:
        """Ingests a single file into the vector store with SHA-256 deduplication."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_id = hashlib.sha256(os.path.abspath(file_path).encode("utf-8")).hexdigest()[:12]
        
        # If reindexing, delete prior chunks for this document
        if reindex:
            self.vector_store.delete_by_document_id(file_id)

        parsed_docs = DocumentParser.parse_file(file_path, default_source_name=source_name)
        total_chunks = 0
        indexed_chunks = 0
        skipped_duplicates = 0

        chunks_to_index = []
        texts_to_embed = []

        # Get set of already indexed hashes
        existing_hashes = self.vector_store.get_indexed_hashes()

        for d_idx, doc in enumerate(parsed_docs):
            doc_identifier = f"{file_id}_d{d_idx}"
            chunks = self.chunker.chunk_document(doc, doc_id=doc_identifier)
            total_chunks += len(chunks)

            for chunk in chunks:
                c_hash = chunk["doc_hash"]
                if c_hash in existing_hashes and not reindex:
                    skipped_duplicates += 1
                    continue

                chunks_to_index.append(chunk)
                texts_to_embed.append(chunk["text"])

        if chunks_to_index:
            embeddings = embedding_service.encode(texts_to_embed)
            self.vector_store.add_documents(chunks_to_index, embeddings)
            indexed_chunks = len(chunks_to_index)
            logger.info(f"[DocumentIngestion] Ingested {indexed_chunks} chunks from {file_path} (Skipped {skipped_duplicates} duplicates)")
        else:
            logger.info(f"[DocumentIngestion] No new chunks to index for {file_path} (All {skipped_duplicates} already indexed)")

        return {
            "file_path": file_path,
            "document_id": file_id,
            "total_chunks": total_chunks,
            "indexed_chunks": indexed_chunks,
            "skipped_duplicates": skipped_duplicates,
            "status": "success"
        }

    def ingest_directory(
        self,
        dir_path: str,
        source_name: str = "Automotive Knowledge",
        recursive: bool = True,
        reindex: bool = False
    ) -> Dict[str, Any]:
        """Recursively ingests all supported documents in a directory."""
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        supported_exts = {".pdf", ".txt", ".md", ".html", ".htm", ".csv", ".json", ".jsonl"}
        results = []
        total_indexed = 0
        total_duplicates = 0

        for root, _, files in os.walk(dir_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in supported_exts:
                    f_path = os.path.join(root, file)
                    try:
                        res = self.ingest_file(f_path, source_name=source_name, reindex=reindex)
                        results.append(res)
                        total_indexed += res["indexed_chunks"]
                        total_duplicates += res["skipped_duplicates"]
                    except Exception as e:
                        logger.error(f"Error ingesting file {f_path}: {e}")
                        results.append({"file_path": f_path, "status": "error", "error": str(e)})
            if not recursive:
                break

        return {
            "directory": dir_path,
            "files_processed": len(results),
            "total_indexed_chunks": total_indexed,
            "total_skipped_duplicates": total_duplicates,
            "details": results
        }
