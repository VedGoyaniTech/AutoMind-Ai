import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.car import Manufacturer, CarModel, CarVariant
from app.models.source import Source
from app.models.ingestion import IngestionJob
from app.repositories.ingestion_repo import IngestionRepository
from app.services.ingestion.validator import DataValidator
from app.services.ingestion.normalizer import DataNormalizer
from app.services.ai.embedding_service import embedding_service
from app.services.ai.vector_store import LocalFAISSVectorStore

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """End-to-end scalable ingestion pipeline handling database writes and vector store sync."""

    def __init__(self, db: Session, vector_store: LocalFAISSVectorStore):
        self.db = db
        self.vector_store = vector_store
        self.repo = IngestionRepository(db)

    def process_records(self, source_name: str, records: List[Dict[str, Any]], job_id: Optional[int] = None) -> IngestionJob:
        if job_id:
            job = self.repo.get_job_by_id(job_id)
        else:
            job = self.repo.create_job(source_name=source_name, total_records=len(records))

        total = len(records)
        processed = 0
        failed = 0
        docs_to_index = []
        texts_to_embed = []

        # Get or create default source
        source_obj = self.db.query(Source).filter(Source.name == source_name).first()
        if not source_obj:
            source_obj = Source(
                name=source_name,
                domain=source_name.lower().replace(" ", "") + ".com",
                base_url=f"https://{source_name.lower().replace(' ', '')}.com",
                source_type="Ingested Dataset",
                reliability_score=0.96
            )
            self.db.add(source_obj)
            self.db.commit()
            self.db.refresh(source_obj)

        for raw_rec in records:
            is_valid, err = DataValidator.validate_record(raw_rec)
            if not is_valid:
                failed += 1
                continue

            try:
                norm = DataNormalizer.normalize_record(raw_rec)
                
                # 1. Manufacturer
                m_name = norm["manufacturer"]
                m_obj = self.db.query(Manufacturer).filter(Manufacturer.name == m_name).first()
                if not m_obj:
                    m_obj = Manufacturer(name=m_name, country=norm.get("country", "Global"))
                    self.db.add(m_obj)
                    self.db.commit()
                    self.db.refresh(m_obj)

                # 2. CarModel
                model_name = norm["model"]
                c_model = self.db.query(CarModel).filter(
                    CarModel.manufacturer_id == m_obj.id,
                    CarModel.name == model_name
                ).first()

                if not c_model:
                    c_model = CarModel(
                        manufacturer_id=m_obj.id,
                        name=model_name,
                        body_type=norm["body_type"]
                    )
                    self.db.add(c_model)
                    self.db.commit()
                    self.db.refresh(c_model)

                # 3. CarVariant (Upsert / Duplicate detection)
                variant_name = norm["variant"]
                v_obj = self.db.query(CarVariant).filter(
                    CarVariant.model_id == c_model.id,
                    CarVariant.variant_name == variant_name,
                    CarVariant.model_year == norm["model_year"]
                ).first()

                if not v_obj:
                    v_obj = CarVariant(
                        model_id=c_model.id,
                        source_id=source_obj.id,
                        variant_name=variant_name,
                        model_year=norm["model_year"],
                        ex_showroom_price=norm["ex_showroom_price"],
                        estimated_on_road_price=norm["estimated_on_road_price"],
                        currency=norm.get("currency", "INR"),
                        country=norm.get("country", "India"),
                        fuel_type=norm["fuel_type"],
                        transmission=norm["transmission"],
                        engine_cc=norm.get("engine_cc"),
                        horsepower=norm.get("horsepower"),
                        torque_nm=norm.get("torque_nm"),
                        combined_mileage=norm.get("combined_mileage"),
                        electric_range=norm.get("electric_range"),
                        seating_capacity=norm["seating_capacity"],
                        airbags=norm["airbags"],
                        safety_rating=norm.get("safety_rating"),
                        boot_space=norm.get("boot_space"),
                        ground_clearance=norm.get("ground_clearance"),
                        drive_type=norm.get("drive_type", "FWD"),
                        description=norm.get("description", f"{m_name} {model_name} {variant_name} with premium performance and features."),
                        image_url=norm.get("image_url"),
                        source_url=norm.get("source_url") or f"{source_obj.base_url}/cars/{m_name.lower()}-{model_name.lower()}"
                    )
                    self.db.add(v_obj)
                    self.db.commit()
                    self.db.refresh(v_obj)

                processed += 1

                # Build document string for vector indexing
                doc_summary = f"{m_name} {model_name} {variant_name} {norm['body_type']} {norm['fuel_type']} {norm['transmission']} Price: ₹{norm['ex_showroom_price']} Airbags: {norm['airbags']} Mileage: {norm.get('combined_mileage')} Safety: {norm.get('safety_rating')} Star. {norm.get('description', '')}"
                
                doc_meta = {
                    "car_variant_id": v_obj.id,
                    "manufacturer": m_name,
                    "model": model_name,
                    "variant": variant_name,
                    "body_type": norm["body_type"],
                    "fuel_type": norm["fuel_type"],
                    "ex_showroom_price": norm["ex_showroom_price"],
                    "source_info": {
                        "id": source_obj.id,
                        "name": source_obj.name,
                        "domain": source_obj.domain,
                        "base_url": source_obj.base_url,
                        "reliability_score": source_obj.reliability_score
                    }
                }

                docs_to_index.append(doc_meta)
                texts_to_embed.append(doc_summary)

            except Exception as e:
                logger.error(f"Error ingesting record: {e}")
                failed += 1

        # Batch vector embedding & store update
        if texts_to_embed:
            embeddings = embedding_service.encode(texts_to_embed)
            self.vector_store.add_documents(docs_to_index, embeddings)

        status = "Completed" if failed == 0 else ("Completed with warnings" if processed > 0 else "Failed")
        return self.repo.update_progress(
            job_id=job.id,
            processed=processed,
            failed=failed,
            total=total,
            status=status
        )
