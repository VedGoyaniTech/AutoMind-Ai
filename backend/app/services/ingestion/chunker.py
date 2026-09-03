import re
import hashlib
from typing import List, Dict, Any, Optional
from app.core.config import settings

class RecursiveDocumentChunker:
    """
    Splits long unstructured documents into semantic overlapping chunks,
    preserving document title, section context, and generating deterministic SHA-256 hashes.
    """

    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: Dict[str, Any], doc_id: str) -> List[Dict[str, Any]]:
        """
        Takes an extracted document dict with 'title', 'text', 'source_url', 'source_name', 'document_type',
        and splits it into chunks.
        """
        title = doc.get("title", "Automotive Document").strip()
        text = doc.get("text", "").strip()
        source_url = doc.get("source_url")
        source_name = doc.get("source_name", "AutoMind Knowledge Base")
        doc_type = doc.get("document_type", "article")
        meta = doc.get("metadata", {})

        if not text:
            return []

        # If text is small enough, return as single chunk
        if len(text) <= self.chunk_size:
            chunk_text = text
            chunk_hash = hashlib.sha256(f"{doc_id}_0_{chunk_text}".encode("utf-8")).hexdigest()
            return [{
                "chunk_id": f"{doc_id}_c0",
                "document_id": doc_id,
                "doc_hash": chunk_hash,
                "title": title,
                "text": chunk_text,
                "source_url": source_url,
                "source_name": source_name,
                "document_type": doc_type,
                "language": "en",
                "reliability_score": 0.92,
                "metadata": meta,
                "doc_type": "knowledge_chunk"
            }]

        # Split by paragraph boundaries first, then sentences if necessary
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If single paragraph exceeds chunk size, split by sentences
            if len(para) > self.chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if current_length + len(sent) > self.chunk_size and current_chunk:
                        chunk_str = " ".join(current_chunk).strip()
                        chunks.append(chunk_str)
                        # Retain overlap from end of current chunk
                        overlap_words = chunk_str.split()[-max(1, self.chunk_overlap // 6):]
                        current_chunk = [" ".join(overlap_words), sent]
                        current_length = sum(len(x) for x in current_chunk) + len(current_chunk)
                    else:
                        current_chunk.append(sent)
                        current_length += len(sent) + 1
            else:
                if current_length + len(para) > self.chunk_size and current_chunk:
                    chunk_str = "\n\n".join(current_chunk).strip()
                    chunks.append(chunk_str)
                    # Retain overlap
                    overlap_words = chunk_str.split()[-max(1, self.chunk_overlap // 6):]
                    current_chunk = [" ".join(overlap_words), para]
                    current_length = sum(len(x) for x in current_chunk) + len(current_chunk)
                else:
                    current_chunk.append(para)
                    current_length += len(para) + 2

        if current_chunk:
            chunks.append("\n\n".join(current_chunk).strip())

        # Build chunk metadata objects
        chunk_objects = []
        for idx, c_text in enumerate(chunks):
            chunk_hash = hashlib.sha256(f"{doc_id}_{idx}_{c_text}".encode("utf-8")).hexdigest()
            # Prefix title for standalone semantic retrieval clarity
            augmented_text = f"[{title}]\n{c_text}" if not c_text.startswith(f"[{title}]") else c_text

            chunk_objects.append({
                "chunk_id": f"{doc_id}_c{idx}",
                "document_id": doc_id,
                "doc_hash": chunk_hash,
                "title": f"{title} (Part {idx + 1})" if len(chunks) > 1 else title,
                "text": augmented_text,
                "source_url": source_url,
                "source_name": source_name,
                "document_type": doc_type,
                "language": "en",
                "reliability_score": 0.92,
                "metadata": meta,
                "doc_type": "knowledge_chunk"
            })

        return chunk_objects
