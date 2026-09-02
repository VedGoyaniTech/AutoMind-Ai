from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class IngestionJobResponse(BaseModel):
    id: int
    source_name: str
    status: str
    total_records: int
    processed_records: int
    failed_records: int
    progress_percentage: float
    error_log: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class IngestionStartRequest(BaseModel):
    source_name: str
    record_count: Optional[int] = 10000
