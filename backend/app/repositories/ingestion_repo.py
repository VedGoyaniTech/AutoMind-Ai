from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.ingestion import IngestionJob

class IngestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, source_name: str, total_records: int = 0) -> IngestionJob:
        job = IngestionJob(
            source_name=source_name,
            status="Pending",
            total_records=total_records,
            processed_records=0,
            failed_records=0,
            progress_percentage=0.0
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_progress(self, job_id: int, processed: int, failed: int, total: int, status: str = "Processing", error: Optional[str] = None) -> Optional[IngestionJob]:
        job = self.db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            job.processed_records = processed
            job.failed_records = failed
            job.total_records = total
            job.status = status
            if total > 0:
                job.progress_percentage = round((processed / total) * 100.0, 2)
            if error:
                job.error_log = error
            if status in ["Completed", "Failed"]:
                job.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(job)
        return job

    def get_job_by_id(self, job_id: int) -> Optional[IngestionJob]:
        return self.db.query(IngestionJob).filter(IngestionJob.id == job_id).first()

    def get_recent_jobs(self, limit: int = 10) -> List[IngestionJob]:
        return self.db.query(IngestionJob).order_by(desc(IngestionJob.started_at)).limit(limit).all()
