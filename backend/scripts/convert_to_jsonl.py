import os
import sys
import json
import sqlite3

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUT_JSONL = os.path.join(DATA_DIR, "finetune_dataset.jsonl")
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "automind_local.db")

def convert_cars_to_jsonl():
    os.makedirs(DATA_DIR, exist_ok=True)
    records = []

    # Attempt 1: Try SQLAlchemy if available
    try:
        from app.db.session import SessionLocal
        from app.models.car import CarVariant
        db = SessionLocal()
        variants = db.query(CarVariant).all()
        for v in variants:
            m_name = v.car_model.manufacturer.name
            model_name = v.car_model.name
            var_name = v.variant_name
            price_lakh = round(v.ex_showroom_price / 100000.0, 2)
            on_road_lakh = round(v.estimated_on_road_price / 100000.0, 2)

            inst1 = {
                "instruction": f"What are the full specifications, price, and features of {m_name} {model_name} {var_name}?",
                "input": "",
                "output": (
                    f"The {m_name} {model_name} ({var_name}) is a {v.car_model.body_type} equipped with a "
                    f"{v.fuel_type} engine and {v.transmission} transmission. "
                    f"Ex-showroom price is ₹{price_lakh} Lakh (Estimated on-road: ₹{on_road_lakh} Lakh). "
                    f"Safety & Specs: {v.airbags} airbags, {v.safety_rating or 'N/A'}-star safety rating, "
                    f"seating capacity of {v.seating_capacity} passengers. {v.description or ''}"
                )
            }
            records.append(inst1)
        db.close()
    except Exception as e:
        print(f"SQLAlchemy notice ({e}). Reading directly from local SQLite database...")
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT variant_name, ex_showroom_price, estimated_on_road_price, fuel_type, transmission, airbags, safety_rating, description FROM car_variants")
            rows = cursor.fetchall()
            for row in rows:
                var_name, price, on_road, fuel, trans, airbags, safety, desc = row
                price_lakh = round((price or 1000000) / 100000.0, 2)
                inst = {
                    "instruction": f"What are the specs and price of vehicle variant {var_name}?",
                    "input": "",
                    "output": f"The {var_name} is priced at ₹{price_lakh} Lakh ex-showroom. Features: {fuel} engine, {trans} transmission, {airbags} airbags, {safety or 5.0}-star safety rating. {desc or ''}"
                }
                records.append(inst)
            conn.close()

    # Default fallback sample data if empty database
    if not records:
        print("Populating default automotive instruction dataset...")
        sample_vehicles = [
            ("Tata", "Nexon", "Creative Plus Petrol", 1150000, "Petrol", "Manual", 6, 5.0),
            ("Tata", "Nexon EV", "Empowered Plus LR", 1699000, "EV", "Automatic", 6, 5.0),
            ("Hyundai", "Creta", "SX (O) 1.5 Turbo DCT", 2000000, "Petrol", "DCT", 6, 4.5),
            ("Kia", "Seltos", "GTX Plus 1.5 Diesel AT", 1980000, "Diesel", "Automatic", 6, 4.0),
            ("Mahindra", "XUV400 EV", "EL Pro 39.4 kWh", 1749000, "EV", "Automatic", 6, 5.0),
            ("BMW", "X5", "xDrive40i M Sport", 9600000, "Petrol", "Automatic", 8, 5.0),
            ("Toyota", "Fortuner", "2.8 Diesel 4x4 AT", 3950000, "Diesel", "Automatic", 7, 5.0),
        ]
        for m, mod, var, price, fuel, trans, airbags, safety in sample_vehicles:
            p_lakh = round(price / 100000.0, 2)
            records.append({
                "instruction": f"What are the specifications and price of {m} {mod} {var}?",
                "input": "",
                "output": f"The {m} {mod} {var} is priced at ₹{p_lakh} Lakh ex-showroom. Specifications: {fuel} engine, {trans} transmission, {airbags} airbags, {safety}-star safety rating."
            })

    # Write to JSONL
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Successfully generated {len(records)} JSONL instruction pairs!")
    print(f"File saved to: {os.path.abspath(OUTPUT_JSONL)}")

if __name__ == "__main__":
    convert_cars_to_jsonl()
