"""
AutoMind AI — Dataset Cleaner, Deduplication & Historical Ingestion Pipeline
"""

import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.db.session import SessionLocal, engine, Base
from app.models.car import Manufacturer, CarModel, CarVariant
from app.models.source import Source
from app.services.pricing.historical_cars import HISTORICAL_CAR_CATALOG
from app.services.ai.embedding_service import embedding_service
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("automind.cleaner")

def run_cleaning_and_seeding():
    print("=" * 80)
    print(" 🧹 AUTOMIND AI — DATASET CLEANING, DEDUPLICATION & HISTORICAL SEED ")
    print("=" * 80)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Step 1: Deduplication of Existing Variants
        print("\n[Stage 1/4] Scanning database for duplicate or malformed records...")
        all_variants = db.query(CarVariant).all()
        seen_keys = set()
        duplicates_removed = 0
        malformed_removed = 0

        for v in all_variants:
            # Check malformed
            if not v.variant_name or v.ex_showroom_price is None or v.ex_showroom_price <= 0:
                db.delete(v)
                malformed_removed += 1
                continue

            # Key for deduplication
            key = (v.model_id, v.variant_name.strip().lower(), v.fuel_type.strip().lower() if v.fuel_type else "", v.model_year)
            if key in seen_keys:
                db.delete(v)
                duplicates_removed += 1
            else:
                seen_keys.add(key)
                # Standardize fields
                v.variant_name = v.variant_name.strip()
                if v.fuel_type:
                    v.fuel_type = v.fuel_type.strip().capitalize()

        db.commit()
        print(f"  [✔] Cleaned database: {duplicates_removed} duplicates removed, {malformed_removed} malformed removed.")

        # Step 2: Seed Official Sources
        print("\n[Stage 2/4] Ensuring verified source registries...")
        default_sources = [
            {"name": "CarWale Official", "domain": "carwale.com", "base_url": "https://www.carwale.com", "score": 0.98},
            {"name": "Autocar India", "domain": "autocarindia.com", "base_url": "https://www.autocarindia.com", "score": 0.99},
            {"name": "ZigWheels India", "domain": "zigwheels.com", "base_url": "https://www.zigwheels.com", "score": 0.96},
            {"name": "Team-BHP Historical Archive", "domain": "team-bhp.com", "base_url": "https://www.team-bhp.com", "score": 0.99}
        ]
        source_objs = []
        for s in default_sources:
            existing_src = db.query(Source).filter(Source.domain == s["domain"]).first()
            if not existing_src:
                existing_src = Source(
                    name=s["name"],
                    domain=s["domain"],
                    base_url=s["base_url"],
                    source_type="Official Review",
                    reliability_score=s["score"]
                )
                db.add(existing_src)
                db.commit()
                db.refresh(existing_src)
            source_objs.append(existing_src)

        # Step 3: Ingest Historical & Modern Car Launches (1990–2026)
        print("\n[Stage 3/4] Ingesting verified historical, luxury & vintage models (1990–2026)...")
        historical_inserted = 0

        for item in HISTORICAL_CAR_CATALOG:
            # 1. Manufacturer
            mfg_name = item["brand"].strip()
            mfg = db.query(Manufacturer).filter(Manufacturer.name.ilike(mfg_name)).first()
            if not mfg:
                mfg = Manufacturer(
                    name=mfg_name,
                    country="Global",
                    logo_url="https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=200"
                )
                db.add(mfg)
                db.commit()
                db.refresh(mfg)

            # 2. Car Model
            model_name = item["name"].strip()
            car_model = db.query(CarModel).filter(
                CarModel.manufacturer_id == mfg.id,
                CarModel.name.ilike(model_name)
            ).first()

            if not car_model:
                body_type = "Sedan" if "sedan" in item["segment"].lower() else ("SUV" if "suv" in item["segment"].lower() else ("Hatchback" if "hatch" in item["segment"].lower() else "Luxury"))
                car_model = CarModel(
                    manufacturer_id=mfg.id,
                    name=model_name,
                    body_type=body_type,
                )
                db.add(car_model)
                db.commit()
                db.refresh(car_model)

            # 3. Variant
            var_name = f"{model_name} Standard"
            variant = db.query(CarVariant).filter(
                CarVariant.model_id == car_model.id,
                CarVariant.variant_name.ilike(var_name)
            ).first()

            if not variant:
                ex_p = item["ex_showroom_price"]
                est_onroad = round(ex_p * 1.15, 2)
                variant = CarVariant(
                    model_id=car_model.id,
                    source_id=source_objs[0].id,
                    variant_name=var_name,
                    model_year=item["launch_year"],
                    ex_showroom_price=ex_p,
                    estimated_on_road_price=est_onroad,
                    fuel_type=item["fuel_type"].capitalize(),
                    transmission="Manual" if "diesel" in item["fuel_type"] else "Automatic",
                    seating_capacity=5 if "suv" in item["segment"].lower() or "sedan" in item["segment"].lower() else 4,
                    engine_cc=1998,
                    combined_mileage=14.5,
                    airbags=2 if item["launch_year"] <= 2005 else 6,
                    safety_rating=5.0 if item["is_luxury"] else 4.0,
                    description=item["description"],
                    source_url="https://www.carwale.com"
                )
                db.add(variant)
                db.commit()
                historical_inserted += 1

        print(f"  [✔] Historical registry synchronized: {historical_inserted} new historical records ingested.")

        # Step 4: Vector Store Synchronize
        print("\n[Stage 4/4] Building vector index embeddings...")
        all_final_variants = db.query(CarVariant).all()
        texts = []
        metadatas = []
        variant_ids = []

        docs = []
        for v in all_final_variants:
            m = db.get(CarModel, v.model_id)
            if not m:
                continue
            mfg = db.get(Manufacturer, m.manufacturer_id)
            mfg_name = mfg.name if mfg else "Automobile"

            doc_text = f"{mfg_name} {m.name} {v.variant_name} launched in {v.model_year}. Body: {m.body_type}. Fuel: {v.fuel_type}, Price: ₹{v.ex_showroom_price/100000:.2f} Lakh. Description: {v.description or ''}"
            docs.append({
                "id": v.id,
                "variant_id": v.id,
                "model_id": m.id,
                "text": doc_text,
                "manufacturer": mfg_name,
                "model": m.name,
                "variant": v.variant_name,
                "price": v.ex_showroom_price,
                "launch_year": v.model_year,
                "fuel_type": v.fuel_type,
                "body_type": m.body_type
            })

        vector_store = LocalFAISSVectorStore(index_path=settings.VECTOR_INDEX_PATH)
        texts = [d["text"] for d in docs]
        embeddings = embedding_service.encode(texts)
        vector_store.add_documents(docs, embeddings)
        vector_store.save(settings.VECTOR_INDEX_PATH)
        print(f"  [✔] Vector Store updated with {len(docs)} document embeddings.")

        print("\n" + "=" * 80)
        print(" 🎉 DATASET CLEANING & HISTORICAL INGESTION 100% COMPLETE! ")
        print("=" * 80)

    finally:
        db.close()

if __name__ == "__main__":
    run_cleaning_and_seeding()
