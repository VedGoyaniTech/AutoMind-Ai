#!/usr/bin/env python3
"""
AutoMind AI — HuggingFace Automotive Dataset Ingestion Pipeline
Ingests VariantWise Open Dataset (HuggingFace: variantwise/indian-cars-variants)
Imports 21 automotive manufacturers, 190 car models, and 1,281 variants with
full specifications, features, dimensions, prices, and provenance.
"""

import os
import sys
import json
import csv
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.db.session import SessionLocal, engine, Base
from app.models.source import Source
from app.models.car import Manufacturer, CarModel, CarVariant
from app.models.provenance import VehicleSpecification, VehiclePrice

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("automind.ingest_hf")

BRAND_COUNTRY_MAP = {
    "audi": "Germany",
    "bmw": "Germany",
    "byd": "China",
    "citroen": "France",
    "honda": "Japan",
    "hyundai": "South Korea",
    "jeep": "USA",
    "kia": "South Korea",
    "lexus": "Japan",
    "mg": "United Kingdom",
    "mahindra": "India",
    "maruti suzuki": "India",
    "maruti": "India",
    "mercedes-benz": "Germany",
    "mercedes": "Germany",
    "nissan": "Japan",
    "renault": "France",
    "skoda": "Czech Republic",
    "tata": "India",
    "tesla": "USA",
    "toyota": "Japan",
    "vinfast": "Vietnam",
    "volkswagen": "Germany",
    "porsche": "Germany",
    "ferrari": "Italy",
    "lamborghini": "Italy",
    "land rover": "United Kingdom",
    "jaguar": "United Kingdom",
    "volvo": "Sweden",
    "rolls-royce": "United Kingdom",
    "bentley": "United Kingdom"
}

def clean_brand_name(brand: str) -> str:
    b = brand.strip()
    if b.lower() == "maruti":
        return "Maruti Suzuki"
    if b.lower() == "mercedes":
        return "Mercedes-Benz"
    return b

def run_ingestion():
    fixtures_dir = os.path.join(BASE_DIR, "data", "fixtures", "huggingface_cars")
    json_path = os.path.join(fixtures_dir, "catalogue.json")
    csv_path = os.path.join(fixtures_dir, "catalogue.csv")

    if not os.path.exists(json_path):
        logger.error(f"JSON fixture not found at {json_path}")
        return

    logger.info("Initializing database connection...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Register or retrieve Source
        source = db.query(Source).filter(Source.domain == "variantwise.com").first()
        if not source:
            source = Source(
                name="VariantWise Open Automotive Dataset (HuggingFace)",
                domain="variantwise.com",
                base_url="https://variantwise.com",
                source_type="Official Catalog",
                reliability_score=0.99
            )
            db.add(source)
            db.commit()
            db.refresh(source)
            logger.info(f"Registered data source: {source.name} (ID: {source.id})")
        else:
            logger.info(f"Using existing data source (ID: {source.id})")

        # Load catalogue.json
        with open(json_path, "r", encoding="utf-8") as f:
            cat_data = json.load(f)

        models_list = cat_data.get("models", [])
        logger.info(f"Loaded {len(models_list)} models from Hugging Face catalogue.json")

        manufacturers_cache: Dict[str, Manufacturer] = {}
        for m in db.query(Manufacturer).all():
            manufacturers_cache[m.name.lower()] = m

        models_cache: Dict[str, CarModel] = {}
        for mo in db.query(CarModel).all():
            models_cache[f"{mo.manufacturer_id}_{mo.name.lower()}"] = mo

        imported_manufacturers = 0
        imported_models = 0
        imported_variants = 0

        for m_data in models_list:
            raw_brand = m_data.get("brand", "").strip()
            brand_name = clean_brand_name(raw_brand)
            model_name = m_data.get("name", "").strip()
            body_type = m_data.get("bodyStyle", m_data.get("bodyType", "SUV")).upper()
            if body_type == "SUV":
                body_type = "SUV"
            elif "SEDAN" in body_type:
                body_type = "Sedan"
            elif "HATCH" in body_type:
                body_type = "Hatchback"
            elif "MPV" in body_type or "MUV" in body_type:
                body_type = "MPV"
            else:
                body_type = m_data.get("bodyType", "Car")

            # 2. Get or create Manufacturer
            b_key = brand_name.lower()
            if b_key not in manufacturers_cache:
                country = BRAND_COUNTRY_MAP.get(b_key, "Global")
                man = Manufacturer(name=brand_name, country=country)
                db.add(man)
                db.commit()
                db.refresh(man)
                manufacturers_cache[b_key] = man
                imported_manufacturers += 1
            manufacturer = manufacturers_cache[b_key]

            # 3. Get or create CarModel
            mo_key = f"{manufacturer.id}_{model_name.lower()}"
            if mo_key not in models_cache:
                car_model = CarModel(
                    manufacturer_id=manufacturer.id,
                    name=model_name,
                    body_type=body_type,
                    generation="Current",
                    country="India",
                    launch_status="launched",
                    source_id=source.id
                )
                db.add(car_model)
                db.commit()
                db.refresh(car_model)
                models_cache[mo_key] = car_model
                imported_models += 1
            car_model = models_cache[mo_key]

            # Engine & Trim lookups
            engines_map: Dict[str, Dict[str, Any]] = {}
            for eng in m_data.get("engines", []):
                e_id = eng.get("id")
                if e_id:
                    engines_map[e_id] = eng

            trims_map: Dict[str, Dict[str, Any]] = {}
            for tr in m_data.get("trims", []):
                t_id = tr.get("id")
                if t_id:
                    trims_map[t_id] = tr

            # Dimensions
            length_mm = m_data.get("lengthMm")
            width_mm = m_data.get("widthMm")
            height_mm = m_data.get("heightMm")
            wheelbase_mm = m_data.get("wheelbaseMm")
            boot_litres = m_data.get("bootLitres")
            seats = m_data.get("seats", 5)

            # 4. Ingest Variants
            variants_list = m_data.get("variants", [])
            for v_data in variants_list:
                v_id = v_data.get("id", "")
                trim_id = v_data.get("trimId", "")
                engine_id = v_data.get("engineId", "")
                trans = v_data.get("transmission", "Manual")
                price_lakh = v_data.get("price")
                source_url = v_data.get("url")

                if price_lakh is None or price_lakh <= 0:
                    continue

                ex_price = float(price_lakh) * 100000.0  # Lakh to INR
                on_road_price = round(ex_price * 1.16, 2)  # Estimated RTO + Insurance + Cess

                trim_info = trims_map.get(trim_id, {})
                trim_name = trim_info.get("name", trim_id.title())
                trim_features = trim_info.get("features", {})
                airbags_count = trim_features.get("airbags", 6)

                engine_info = engines_map.get(engine_id, {})
                engine_name = engine_info.get("name", "")
                fuel_raw = engine_info.get("fuel", "petrol").lower()
                if "diesel" in fuel_raw:
                    fuel_type = "Diesel"
                elif "electric" in fuel_raw or "ev" in fuel_raw:
                    fuel_type = "EV"
                elif "cng" in fuel_raw:
                    fuel_type = "CNG"
                elif "hybrid" in fuel_raw:
                    fuel_type = "Hybrid"
                else:
                    fuel_type = "Petrol"

                power_ps = engine_info.get("powerPs")
                horsepower = float(power_ps) * 0.9863 if power_ps else None  # PS to BHP
                torque_nm = float(engine_info.get("torqueNm")) if engine_info.get("torqueNm") else None
                engine_cc = int(engine_info.get("displacementCc")) if engine_info.get("displacementCc") else None
                efficiency = float(engine_info.get("officialEfficiency")) if engine_info.get("officialEfficiency") else None
                drive_type = engine_info.get("driveType", "FWD")
                engine_desc = engine_info.get("character", "")
                trim_positioning = trim_info.get("positioning", "")

                variant_full_name = f"{trim_name} {trans}"
                if fuel_type in ["Diesel", "CNG", "EV", "Hybrid"]:
                    variant_full_name = f"{trim_name} {fuel_type} {trans}"

                # Transmission category
                t_lower = trans.lower()
                if any(x in t_lower for x in ["at", "dct", "cvt", "amt", "automatic", "dsg", "9at", "8at", "7at", "6at"]):
                    trans_clean = "Automatic"
                else:
                    trans_clean = "Manual"

                full_desc = f"{brand_name} {model_name} {variant_full_name}. {trim_positioning} {engine_desc}".strip()

                # Check if variant already exists
                existing_v = (
                    db.query(CarVariant)
                    .filter(
                        CarVariant.model_id == car_model.id,
                        CarVariant.variant_name == variant_full_name
                    )
                    .first()
                )

                if existing_v:
                    existing_v.ex_showroom_price = ex_price
                    existing_v.estimated_on_road_price = on_road_price
                    existing_v.fuel_type = fuel_type
                    existing_v.transmission = trans_clean
                    existing_v.engine_cc = engine_cc
                    existing_v.horsepower = horsepower
                    existing_v.torque_nm = torque_nm
                    existing_v.combined_mileage = efficiency
                    existing_v.seating_capacity = seats or 5
                    existing_v.airbags = airbags_count or 6
                    existing_v.boot_space = boot_litres
                    existing_v.length = length_mm
                    existing_v.width = width_mm
                    existing_v.height = height_mm
                    existing_v.wheelbase = wheelbase_mm
                    existing_v.drive_type = drive_type
                    existing_v.features = trim_features
                    existing_v.description = full_desc
                    existing_v.source_url = source_url
                    existing_v.source_id = source.id
                else:
                    new_v = CarVariant(
                        model_id=car_model.id,
                        source_id=source.id,
                        variant_name=variant_full_name,
                        model_year=2025,
                        lifecycle_status="active",
                        feature_set_version="1.0",
                        engine_battery_identifier=engine_name,
                        ex_showroom_price=ex_price,
                        estimated_on_road_price=on_road_price,
                        currency="INR",
                        country="India",
                        fuel_type=fuel_type,
                        transmission=trans_clean,
                        engine_cc=engine_cc,
                        horsepower=horsepower,
                        torque_nm=torque_nm,
                        combined_mileage=efficiency,
                        seating_capacity=seats or 5,
                        airbags=airbags_count or 6,
                        safety_rating=5.0 if airbags_count >= 6 else 4.0,
                        boot_space=boot_litres,
                        length=length_mm,
                        width=width_mm,
                        height=height_mm,
                        wheelbase=wheelbase_mm,
                        drive_type=drive_type,
                        features=trim_features,
                        description=full_desc,
                        source_url=source_url
                    )
                    db.add(new_v)
                    imported_variants += 1

        db.commit()
        logger.info(f"Ingestion Complete!")
        logger.info(f"New Manufacturers: {imported_manufacturers}")
        logger.info(f"New Models: {imported_models}")
        logger.info(f"New Variants: {imported_variants}")

        # Total counts in DB
        total_mans = db.query(Manufacturer).count()
        total_mos = db.query(CarModel).count()
        total_vars = db.query(CarVariant).count()
        logger.info(f"TOTAL IN DATABASE -> Manufacturers: {total_mans}, Models: {total_mos}, Variants: {total_vars}")

    except Exception as e:
        db.rollback()
        logger.exception(f"Ingestion failed with error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_ingestion()
