import os
import json
import csv
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class DocumentParser:
    """
    Universal multi-format parser extracting text, title, and metadata from:
    - .pdf (brochures & owner manuals)
    - .txt / .md (markdown articles, release notes, guides)
    - .html (scraped automotive portal articles)
    - .csv (tabular FAQ/spec sheets)
    - .json / .jsonl (instruction/QA datasets & structured documents)
    """

    @classmethod
    def parse_file(cls, file_path: str, default_source_name: str = "Automotive Document") -> List[Dict[str, Any]]:
        """
        Parses a file and returns a list of extracted document sections.
        Each section has: 'title', 'text', 'source_url', 'source_name', 'document_type', 'metadata'.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        file_basename = os.path.basename(file_path)

        if ext in [".txt", ".md", ".markdown"]:
            return cls._parse_text_or_markdown(file_path, default_source_name)
        elif ext == ".pdf":
            return cls._parse_pdf(file_path, default_source_name)
        elif ext in [".html", ".htm"]:
            return cls._parse_html(file_path, default_source_name)
        elif ext == ".csv":
            return cls._parse_csv(file_path, default_source_name)
        elif ext == ".json":
            return cls._parse_json(file_path, default_source_name)
        elif ext == ".jsonl":
            return cls._parse_jsonl(file_path, default_source_name)
        else:
            # Fallback to plain text
            return cls._parse_text_or_markdown(file_path, default_source_name)

    @classmethod
    def _clean_text(cls, text: str) -> str:
        """Normalizes whitespace and removes null bytes or control characters."""
        if not text:
            return ""
        text = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
        # Collapse excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Collapse multiple spaces
        text = re.sub(r'[ \t]{2,}', ' ', text)
        return text.strip()

    @classmethod
    def _parse_text_or_markdown(cls, file_path: str, source_name: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        cleaned = cls._clean_text(content)
        if not cleaned:
            return []

        # Try to find top header as title
        title_match = re.search(r'^#\s+(.+)$', cleaned, flags=re.MULTILINE)
        title = title_match.group(1).strip() if title_match else os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").title()

        doc_type = "manual" if "manual" in file_path.lower() else ("guide" if "guide" in file_path.lower() else "article")

        return [{
            "title": title,
            "text": cleaned,
            "source_url": f"file://{os.path.abspath(file_path)}",
            "source_name": source_name,
            "document_type": doc_type,
            "metadata": {"file_path": file_path, "file_name": os.path.basename(file_path)}
        }]

    @classmethod
    def _parse_pdf(cls, file_path: str, source_name: str) -> List[Dict[str, Any]]:
        text_content = ""
        # Try pypdf / PyPDF2 / pdfplumber if installed
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_content += t + "\n"
        except ImportError:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(file_path)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text_content += t + "\n"
            except Exception as e:
                logger.warning(f"PDF library not available or error parsing {file_path}: {e}")
                # Simple binary string extraction fallback
                with open(file_path, "rb") as f:
                    raw_bytes = f.read()
                text_content = re.sub(rb'[^\x20-\x7E\n]', b' ', raw_bytes).decode('ascii', errors='ignore')

        cleaned = cls._clean_text(text_content)
        title = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").title()
        doc_type = "brochure" if "brochure" in file_path.lower() else "manual"

        return [{
            "title": title,
            "text": cleaned or f"PDF Document: {title}",
            "source_url": f"file://{os.path.abspath(file_path)}",
            "source_name": source_name,
            "document_type": doc_type,
            "metadata": {"file_path": file_path, "file_name": os.path.basename(file_path)}
        }]

    @classmethod
    def _parse_html(cls, file_path: str, source_name: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()

        # Remove scripts and styles
        html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', html, flags=re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else os.path.splitext(os.path.basename(file_path))[0].title()

        # Extract plain text
        plain_text = re.sub(r'<[^>]+>', ' ', html)
        cleaned = cls._clean_text(plain_text)

        return [{
            "title": title,
            "text": cleaned,
            "source_url": f"file://{os.path.abspath(file_path)}",
            "source_name": source_name,
            "document_type": "article",
            "metadata": {"file_path": file_path, "file_name": os.path.basename(file_path)}
        }]

    @classmethod
    def _parse_csv(cls, file_path: str, source_name: str) -> List[Dict[str, Any]]:
        docs = []
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                # Look for common text/question/answer columns
                title = row.get("title") or row.get("question") or row.get("car_name") or f"Record {idx}"
                text_parts = [f"{k}: {v}" for k, v in row.items() if v and str(v).strip()]
                text = " | ".join(text_parts)

                docs.append({
                    "title": str(title),
                    "text": cls._clean_text(text),
                    "source_url": row.get("source_url") or f"file://{os.path.abspath(file_path)}#row={idx}",
                    "source_name": source_name,
                    "document_type": "faq" if "question" in row else "spec_sheet",
                    "metadata": row
                })
        return docs

    @classmethod
    def _parse_json(cls, file_path: str, source_name: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)

        docs = []
        if isinstance(data, list):
            for idx, item in enumerate(data, 1):
                docs.extend(cls._dict_to_doc(item, file_path, source_name, idx))
        elif isinstance(data, dict):
            docs.extend(cls._dict_to_doc(data, file_path, source_name, 1))
        return docs

    @classmethod
    def _parse_jsonl(cls, file_path: str, source_name: str) -> List[Dict[str, Any]]:
        docs = []
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    docs.extend(cls._dict_to_doc(item, file_path, source_name, idx))
                except Exception:
                    continue
        return docs

    @classmethod
    def _dict_to_doc(cls, item: Dict[str, Any], file_path: str, source_name: str, idx: int) -> List[Dict[str, Any]]:
        title = item.get("title") or item.get("instruction") or item.get("question") or item.get("car_name") or f"{os.path.basename(file_path)} #{idx}"
        
        # Determine text body
        if "text" in item and item["text"]:
            text = str(item["text"])
        elif "output" in item and "instruction" in item:
            text = f"Question: {item['instruction']}\nAnswer: {item['output']}"
        elif "response" in item and "prompt" in item:
            text = f"Prompt: {item['prompt']}\nResponse: {item['response']}"
        else:
            text = "\n".join([f"{k}: {v}" for k, v in item.items() if v and not isinstance(v, (dict, list))])

        cleaned = cls._clean_text(text)
        if not cleaned:
            return []

        doc_type = "faq" if "question" in item or "instruction" in item else "article"

        return [{
            "title": str(title),
            "text": cleaned,
            "source_url": item.get("source_url") or f"file://{os.path.abspath(file_path)}#{idx}",
            "source_name": item.get("source_name") or source_name,
            "document_type": doc_type,
            "metadata": item
        }]
