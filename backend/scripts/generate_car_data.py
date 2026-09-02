import sys
import os
import random
import argparse
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine, Base
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.services.ingestion.pipeline import IngestionPipeline
from app.core.config import settings

MANUFACTURERS = ["Tata", "Hyundai", "Kia", "Mahindra", "Maruti", "Toyota", "Honda", "BMW", "Mercedes", "Audi"]
BODY_TYPES = ["SUV", "Sedan", "Hatchback", "MUV", "EV", "Hybrid"]
FUELS = ["Petrol", "Diesel", "EV", "Hybrid", "CNG"]
TRANSMISSIONS = ["Manual", "Automatic", "DCT", "CVT", "AMT"]

def generate_synthetic_data(num_rows: int, output_file: str = None):
    print(f"Generating {num_rows:,} synthetic automotive records...")

    records = []
    for i in range(1, num_rows + 1):
        m = random.choice(MANUFACTURERS)
        b = random.choice(BODY_TYPES)
        fuel = "EV" if b == "EV" else random.choice(FUELS)
        trans = random.choice(TRANSMISSIONS)
        model_num = random.randint(1, 20)
        model_name = f"{m} Series-{model_num}"
        variant_name = f"{fuel} {trans} Spec-{random.randint(100, 999)}"

        price = random.randint(6, 95) * 100000 # 6 Lakh to 95 Lakh
        airbags = random.choice([2, 6, 7, 8])
        mileage = round(random.uniform(12.0, 24.5), 1) if fuel != "EV" else None
        range_ev = round(random.uniform(320.0, 620.0), 1) if fuel == "EV" else None
        safety = round(random.choice([3.5, 4.0, 4.5, 5.0]), 1)

        rec = {
            "manufacturer": m,
            "model": model_name,
            "variant": variant_name,
            "body_type": b,
            "fuel_type": fuel,
            "transmission": trans,
            "ex_showroom_price": price,
            "estimated_on_road_price": int(price * 1.16),
            "model_year": random.choice([2023, 2024, 2025]),
            "seating_capacity": 5 if b != "MUV" else 7,
            "airbags": airbags,
            "combined_mileage": mileage,
            "electric_range": range_ev,
            "safety_rating": safety,
            "description": f"Synthetic high-efficiency vehicle model designed for urban and highway travel with {airbags} airbags and {safety} star safety rating."
        }

        records.append(rec)

    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        print(f"Saved {num_rows:,} records to {output_file}")
    else:
        # Ingest directly into database and vector index in batches
        print("Ingesting generated records into MySQL database and Vector Store...")
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        vector_store = LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
        pipeline = IngestionPipeline(db, vector_store)

        batch_size = settings.INGESTION_BATCH_SIZE
        for idx in range(0, len(records), batch_size):
            chunk = records[idx:idx + batch_size]
            pipeline.process_records(source_name="Synthetic Auto Generator", records=chunk)
            print(f"Ingested batch {idx // batch_size + 1} / {(len(records) + batch_size - 1) // batch_size}...")

        print("Synthetic dataset generation and ingestion complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic Car Data Generator for Million-Record Benchmark")
    parser.add_argument("--rows", type=int, default=1000, help="Number of synthetic car records to generate")
    parser.add_argument("--out", type=str, default=None, help="Optional output JSON file path")
    args = parser.parse_args()

    generate_synthetic_data(num_rows=args.rows, output_file=args.out)
