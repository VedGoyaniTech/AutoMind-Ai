import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import joinedload
from app.db.session import SessionLocal
from app.models.car import CarVariant, CarModel, Manufacturer
from app.services.ai.embedding_service import embedding_service
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.core.config import settings

def build_embeddings():
    print("Reading all car variants from database...")
    db = SessionLocal()
    variants = (
        db.query(CarVariant)
        .options(
            joinedload(CarVariant.car_model).joinedload(CarModel.manufacturer),
            joinedload(CarVariant.source)
        )
        .all()
    )

    if not variants:
        print("No car variants found in database. Seed or import data first.")
        return

    print(f"Generating vector embeddings for {len(variants)} vehicles...")
    docs_to_index = []
    texts_to_embed = []

    for v in variants:
        m_name = v.car_model.manufacturer.name
        model_name = v.car_model.name
        variant_name = v.variant_name
        body_type = v.car_model.body_type

        summary_text = f"{m_name} {model_name} {variant_name} {body_type} {v.fuel_type} {v.transmission} Price: ₹{v.ex_showroom_price} Airbags: {v.airbags} Mileage: {v.combined_mileage} Range: {v.electric_range} Safety: {v.safety_rating} Stars. {v.description or ''}"

        doc_meta = {
            "car_variant_id": v.id,
            "manufacturer": m_name,
            "model": model_name,
            "variant": variant_name,
            "body_type": body_type,
            "fuel_type": v.fuel_type,
            "ex_showroom_price": v.ex_showroom_price,
            "source_info": {
                "id": v.source.id,
                "name": v.source.name,
                "domain": v.source.domain,
                "base_url": v.source.base_url,
                "reliability_score": v.source.reliability_score
            } if v.source else None
        }

        docs_to_index.append(doc_meta)
        texts_to_embed.append(summary_text)

    vector_store = LocalFAISSVectorStore(settings.VECTOR_INDEX_PATH)
    embeddings = embedding_service.encode(texts_to_embed)
    vector_store.add_documents(docs_to_index, embeddings)
    print(f"Successfully generated embeddings and updated vector index at {settings.VECTOR_INDEX_PATH}!")

if __name__ == "__main__":
    build_embeddings()
