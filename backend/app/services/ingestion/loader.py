import csv
import json
from typing import Generator, Dict, Any, List

class BatchDataLoader:
    """Memory-efficient streaming loader for CSV, JSON, and JSONL automotive datasets."""

    @staticmethod
    def stream_csv(file_path: str, batch_size: int = 1000) -> Generator[List[Dict[str, Any]], None, None]:
        batch = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                batch.append(row)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch

    @staticmethod
    def stream_jsonl(file_path: str, batch_size: int = 1000) -> Generator[List[Dict[str, Any]], None, None]:
        batch = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    batch.append(record)
                    if len(batch) >= batch_size:
                        yield batch
                        batch = []
                except json.JSONDecodeError:
                    continue
            if batch:
                yield batch

    @staticmethod
    def stream_json(file_path: str, batch_size: int = 1000) -> Generator[List[Dict[str, Any]], None, None]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            if isinstance(data, dict) and "cars" in data:
                data = data["cars"]
            if isinstance(data, list):
                for i in range(0, len(data), batch_size):
                    yield data[i:i + batch_size]
