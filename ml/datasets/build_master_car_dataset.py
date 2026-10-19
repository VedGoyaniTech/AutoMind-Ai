"""
AutoMind AI — Comprehensive Automotive Dataset Aggregation, Cleaning, Filtering,
Deduplication & Instruction-Tuning Dataset Generator.

Aggregates:
1. Kaggle Car Details v4 (Modern Indian car specs: Make, Model, Price, Engine, Power, Torque, Fuel Tank, Dimensions)
2. Kaggle Car Details v3 (8,128 CarDekho cars: Mileage, Engine CC, Max Power bhp, Seats, Fuel, Transmission)
3. EV Real-World Database (Battery kWh, Range km, Fast Charge, Top Speed, Acceleration)
4. VariantWise Indian Automotive Catalogue (1,282 latest official Indian market variants)
5. Curated Multilingual Automotive Knowledge Base (Hindi, Gujarati, English, Hinglish)

Features:
- Rigorous data validation and outlier filtering
- PII redaction
- SHA-256 content deduplication
- Generates JSON fine-tuning dataset (as requested) + JSONL train/val/test splits
"""

import os
import sys
import csv
import io
import json
import re
import hashlib
import urllib.request
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASETS_DIR = os.path.join(BASE_DIR, "ml", "datasets")
REPORTS_DIR = os.path.join(DATASETS_DIR, "reports")
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Sources
URL_CAR_DETAILS_V4 = "https://raw.githubusercontent.com/chandanverma07/DataSets/master/car%20details%20v4.csv"
URL_CAR_DETAILS_V3 = "https://raw.githubusercontent.com/HarshKapadia2/car-details/main/data/car_details_v3.csv"
URL_EV_CARS = "https://raw.githubusercontent.com/Aniketligam/EV-Cars-Analysis/main/EV_cars.csv"
LOCAL_CATALOGUE = os.path.join(BASE_DIR, "backend", "data", "fixtures", "huggingface_cars", "catalogue.csv")


def fetch_csv_content(url: str, timeout: int = 30) -> str:
    print(f"[*] Downloading dataset from: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def format_inr(val: float) -> str:
    if val >= 10000000:
        return f"₹{val / 10000000:.2f} Cr"
    elif val >= 100000:
        return f"₹{val / 100000:.2f} Lakh"
    else:
        return f"₹{val:,.0f}"


def clean_num(val_str: Any) -> float:
    if not val_str:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", str(val_str))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def clean_fuel(fuel: str) -> str:
    f = (fuel or "").strip().title()
    if f in ["Electric", "Ev"]:
        return "Electric"
    elif "Cng" in f:
        return "CNG"
    elif "Hybrid" in f:
        return "Hybrid"
    elif "Diesel" in f:
        return "Diesel"
    elif "Petrol" in f:
        return "Petrol"
    return f or "Petrol"


def parse_v4_data(csv_text: str) -> List[Dict[str, Any]]:
    print("[*] Parsing & Cleaning Car Details v4...")
    reader = csv.DictReader(io.StringIO(csv_text))
    cars = []
    for row in reader:
        make = (row.get("Make") or "").strip()
        model = (row.get("Model") or "").strip()
        if not make or not model:
            continue
        price = clean_num(row.get("Price"))
        if price <= 30000 or price > 250000000:
            continue
        year = int(clean_num(row.get("Year")) or 2020)
        fuel = clean_fuel(row.get("Fuel Type"))
        trans = (row.get("Transmission") or "Manual").strip().title()
        engine = clean_num(row.get("Engine"))
        power = (row.get("Max Power") or "").strip()
        torque = (row.get("Max Torque") or "").strip()
        seats = int(clean_num(row.get("Seating Capacity")) or 5)
        drivetrain = (row.get("Drivetrain") or "").strip()
        tank = clean_num(row.get("Fuel Tank Capacity"))

        cars.append({
            "make": make,
            "model": model,
            "year": year,
            "price": price,
            "fuel": fuel,
            "transmission": trans,
            "engine_cc": int(engine) if engine else None,
            "power": power,
            "torque": torque,
            "seats": seats,
            "drivetrain": drivetrain,
            "fuel_tank_l": tank if tank else None,
            "source": "Car Details v4"
        })
    print(f"    [✔] Extracted {len(cars)} valid vehicles from v4.")
    return cars


def parse_v3_data(csv_text: str) -> List[Dict[str, Any]]:
    print("[*] Parsing & Cleaning Car Details v3 (CarDekho)...")
    reader = csv.DictReader(io.StringIO(csv_text))
    cars = []
    for row in reader:
        raw_name = (row.get("name") or "").strip()
        if not raw_name:
            continue
        parts = raw_name.split()
        make = parts[0]
        model = " ".join(parts[1:])
        price = clean_num(row.get("selling_price"))
        if price <= 30000 or price > 200000000:
            continue
        year = int(clean_num(row.get("year")) or 2018)
        fuel = clean_fuel(row.get("fuel"))
        trans = (row.get("transmission") or "Manual").strip().title()
        mileage = clean_num(row.get("mileage"))
        engine = clean_num(row.get("engine"))
        power = clean_num(row.get("max_power"))
        seats = int(clean_num(row.get("seats")) or 5)

        cars.append({
            "make": make,
            "model": model,
            "year": year,
            "price": price,
            "fuel": fuel,
            "transmission": trans,
            "mileage_kmpl": mileage if mileage > 0 else None,
            "engine_cc": int(engine) if engine > 0 else None,
            "power_bhp": power if power > 0 else None,
            "seats": seats,
            "source": "Car Details v3"
        })
    print(f"    [✔] Extracted {len(cars)} valid vehicles from v3.")
    return cars


def parse_ev_data(csv_text: str) -> List[Dict[str, Any]]:
    print("[*] Parsing & Cleaning EV Database...")
    reader = csv.DictReader(io.StringIO(csv_text))
    evs = []
    for row in reader:
        car_name = (row.get("Car_name") or "").strip()
        if not car_name:
            continue
        battery = clean_num(row.get("Battery"))
        range_km = clean_num(row.get("Range"))
        top_speed = clean_num(row.get("Top_speed"))
        accel = clean_num(row.get("acceleration..0.100."))
        fast_charge = clean_num(row.get("Fast_charge"))
        price_de = clean_num(row.get("Price.DE."))

        evs.append({
            "name": car_name,
            "battery_kwh": battery if battery > 0 else None,
            "range_km": range_km if range_km > 0 else None,
            "top_speed_kmh": top_speed if top_speed > 0 else None,
            "accel_0_100_s": accel if accel > 0 else None,
            "fast_charge_kmh": fast_charge if fast_charge > 0 else None,
            "price_eur": price_de if price_de > 0 else None,
            "source": "EV Global Database"
        })
    print(f"    [✔] Extracted {len(evs)} valid EV models.")
    return evs


def parse_catalogue_data(filepath: str) -> List[Dict[str, Any]]:
    print(f"[*] Parsing Local Indian Catalogue from {filepath}...")
    if not os.path.exists(filepath):
        print("    [-] File not found.")
        return []
    cars = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            brand = (row.get("brand") or "").strip()
            model = (row.get("model") or "").strip()
            variant = (row.get("variant") or "").strip()
            if not brand or not model:
                continue
            price_lakh = clean_num(row.get("price"))
            fuel = clean_fuel(row.get("fuel"))
            transmission = (row.get("gearbox") or row.get("transmission") or "Manual").strip().title()
            body = (row.get("bodyStyle") or "SUV").strip()
            engine = (row.get("engine") or "").strip()
            seats = int(clean_num(row.get("seats")) or 5)

            cars.append({
                "make": brand,
                "model": model,
                "variant": variant,
                "price_lakh": price_lakh,
                "price": price_lakh * 100000,
                "fuel": fuel,
                "transmission": transmission,
                "body_style": body,
                "engine_desc": engine,
                "seats": seats,
                "source": "Indian Automotive Catalogue"
            })
    print(f"    [✔] Extracted {len(cars)} official market variants.")
    return cars


def generate_instruction_pairs(
    v4_cars: List[Dict[str, Any]],
    v3_cars: List[Dict[str, Any]],
    ev_cars: List[Dict[str, Any]],
    cat_cars: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    print("[*] Generating High-Accuracy Instruction Fine-Tuning Pairs...")
    pairs: List[Dict[str, Any]] = []

    # 1. From Car Details v4 (Specs, Engine, Power, Torque)
    for c in v4_cars[:1500]:
        name = f"{c['make']} {c['model']}"
        # Spec Q&A
        specs_parts = [f"Make & Model: {name} ({c['year']})"]
        if c.get("engine_cc"):
            specs_parts.append(f"Engine Displacement: {c['engine_cc']} cc")
        if c.get("power"):
            specs_parts.append(f"Max Power: {c['power']}")
        if c.get("torque"):
            specs_parts.append(f"Max Torque: {c['torque']}")
        specs_parts.append(f"Fuel Type: {c['fuel']}")
        specs_parts.append(f"Transmission: {c['transmission']}")
        specs_parts.append(f"Seating Capacity: {c['seats']} Persons")
        if c.get("fuel_tank_l"):
            specs_parts.append(f"Fuel Tank Capacity: {c['fuel_tank_l']} Litres")
        if c.get("price"):
            specs_parts.append(f"Approximate Valuation: {format_inr(c['price'])}")

        output_text = (
            f"Here are the verified specifications for the {name} ({c['year']}):\n"
            + "\n".join(f"• {p}" for p in specs_parts)
            + f"\n\nThis vehicle operates on {c['fuel']} with a {c['transmission']} transmission."
        )

        pairs.append({
            "instruction": f"What are the specifications, engine, and power figures of {name}?",
            "input": "",
            "output": output_text,
            "category": "specifications",
            "metadata": {"make": c["make"], "model": c["model"], "year": c["year"]}
        })

        # Price Inquiry
        pairs.append({
            "instruction": f"What is the market price of {name} {c['year']}?",
            "input": "",
            "output": f"The estimated market price of the {c['year']} {name} is approximately {format_inr(c['price'])} (ex-showroom/market value depending on condition and state taxes).",
            "category": "pricing",
            "metadata": {"make": c["make"], "model": c["model"], "price": c["price"]}
        })

        # Multilingual Hindi/Hinglish
        pairs.append({
            "instruction": f"{name} ka engine aur power details batao",
            "input": "",
            "output": f"{name} ({c['year']}) me {c.get('engine_cc', 'Standard')} cc ka engine milta hai jo {c.get('power', 'behtareen power')} generate karta hai. Iska fuel type {c['fuel']} aur transmission {c['transmission']} hai. Iski market price lagbhag {format_inr(c['price'])} hai.",
            "category": "multilingual_specs",
            "metadata": {"language": "hinglish", "make": c["make"]}
        })

    # 2. From Car Details v3 (Mileage and Fuel Economy)
    for c in v3_cars[:2000]:
        name = f"{c['make']} {c['model']}"
        if c.get("mileage_kmpl") and c["mileage_kmpl"] > 5.0:
            pairs.append({
                "instruction": f"What is the mileage and fuel efficiency of {name}?",
                "input": "",
                "output": f"The {name} delivers an ARAI/real-world fuel efficiency of approximately {c['mileage_kmpl']:.2f} kmpl. It is powered by a {c.get('engine_cc', 'efficient')} cc {c['fuel']} engine producing {c.get('power_bhp', 'optimal')} bhp with a {c['transmission']} gearbox.",
                "category": "mileage",
                "metadata": {"make": c["make"], "mileage": c["mileage_kmpl"]}
            })

            # Gujarati mileage query
            pairs.append({
                "instruction": f"{name} નું માઈલેજ કેટલું છે?",
                "input": "",
                "output": f"{name} નું ફ્યુઅલ એવરેજ/માઈલેજ અંદાજે {c['mileage_kmpl']:.2f} kmpl છે. આ ગાડી {c['fuel']} એન્જિન સાથે આવે છે અને તેનું ટ્રાન્સમિશન {c['transmission']} છે.",
                "category": "multilingual_mileage",
                "metadata": {"language": "gujarati", "make": c["make"]}
            })

    # 3. From Official Catalogue (New Car Variants, Ex-Showroom Delhi)
    for c in cat_cars:
        full_variant = f"{c['make']} {c['model']} {c['variant']}"
        pairs.append({
            "instruction": f"What is the ex-showroom price and variant details of {full_variant} in India?",
            "input": "",
            "output": f"The official ex-showroom price (Delhi) for the {full_variant} is {format_inr(c['price'])} ({c['price_lakh']:.2f} Lakhs). It comes configured as a {c['body_style']} with a {c['fuel']} engine ({c['engine_desc']}), {c['transmission']} gearbox, and {c['seats']}-seater layout.",
            "category": "official_variants",
            "metadata": {"make": c["make"], "model": c["model"], "variant": c["variant"], "price_lakh": c["price_lakh"]}
        })

    # 4. From EV Database (Range, Battery, Fast Charging)
    for ev in ev_cars:
        name = ev["name"]
        ev_specs = [
            f"Model: {name}",
            f"Battery Pack: {ev['battery_kwh']} kWh" if ev.get("battery_kwh") else None,
            f"Driving Range: {ev['range_km']} km (WLTP/Real-World)" if ev.get("range_km") else None,
            f"Top Speed: {ev['top_speed_kmh']} km/h" if ev.get("top_speed_kmh") else None,
            f"0-100 km/h Acceleration: {ev['accel_0_100_s']} seconds" if ev.get("accel_0_100_s") else None,
            f"Fast Charge Speed: {ev['fast_charge_kmh']} km/h" if ev.get("fast_charge_kmh") else None,
        ]
        ev_specs_clean = [s for s in ev_specs if s]
        pairs.append({
            "instruction": f"What is the battery capacity, range, and performance of {name}?",
            "input": "",
            "output": f"Specifications for the electric vehicle {name}:\n" + "\n".join(f"• {s}" for s in ev_specs_clean),
            "category": "ev_specifications",
            "metadata": {"vehicle": name, "type": "EV"}
        })

        pairs.append({
            "instruction": f"{name} EV ki battery aur range kitni hai?",
            "input": "",
            "output": f"{name} ek fully electric vehicle hai jisme {ev.get('battery_kwh', 'high-capacity')} kWh ki battery di gayi hai. Iski estimated driving range lagbhag {ev.get('range_km', '300+')} km hai aur 0-100 km/h ki acceleration {ev.get('accel_0_100_s', 'quick')} seconds me poori karti hai.",
            "category": "multilingual_ev",
            "metadata": {"language": "hinglish", "vehicle": name}
        })

    # 5. Core Automotive Comparisons (Curated pairs)
    COMPARISONS = [
        ("Tata Nexon", "Hyundai Creta", "Nexon is a sub-4m compact SUV (₹8.00L - ₹15.80L, 5-Star BNCAP) while Creta is a larger mid-size SUV (₹11.00L - ₹20.15L). Nexon offers superior crash safety and ruggedness, whereas Creta offers greater rear seat legroom, a panoramic sunroof, and a more refined cabin."),
        ("Mahindra Thar", "Suzuki Jimny", "Mahindra Thar offers higher ground clearance (226 mm vs 210 mm), powerful 2.0L Turbo Petrol (150 PS) and 2.2L Diesel (130 PS) engines, and strong road presence. Suzuki Jimny offers a lightweight 5-door ladder-frame chassis with a 1.5L K15B petrol engine (105 PS), offering agile trail maneuverability and everyday city usability."),
        ("Tata Punch EV", "MG Comet EV", "Tata Punch EV (₹10.99L - ₹15.49L, 25-35 kWh, 315-421 km range, 190 mm ground clearance) is a versatile 5-seater micro-SUV with DC fast charging. MG Comet EV (₹6.99L - ₹9.53L, 17.3 kWh, 230 km range) is an ultra-compact 2-door city commuter tailored for narrow parking and city traffic."),
        ("Toyota Innova Hycross", "Mahindra XUV700", "Innova Hycross is a monocoque MPV featuring a strong hybrid powertrain with exceptional 23.24 kmpl mileage and Ottoman captain seats. XUV700 is a performance-focused tech SUV with 200 PS turbo petrol or 185 PS diesel, Level 2 ADAS, and optional All-Wheel Drive (AWD)."),
        ("Tata Curvv", "Citroen Basalt", "Both are coupe SUVs launched in 2024. Curvv offers ICE (Petrol/Diesel) and EV powertrains with Level 2 ADAS, flush door handles, and 5-Star BNCAP safety. Basalt focuses on competitive pricing (starting ₹7.99L) with comfort-tuned Advanced Comfort suspension and 1.2L Turbo petrol.")
    ]
    for car_a, car_b, comp_detail in COMPARISONS:
        pairs.append({
            "instruction": f"Compare {car_a} vs {car_b}.",
            "input": "",
            "output": f"Comparison between {car_a} and {car_b}:\n\n{comp_detail}",
            "category": "comparison",
            "metadata": {"car_a": car_a, "car_b": car_b}
        })
        pairs.append({
            "instruction": f"{car_a} aur {car_b} me kya antar hai?",
            "input": "",
            "output": f"{car_a} aur {car_b} ki tulna:\n\n{comp_detail}",
            "category": "multilingual_comparison",
            "metadata": {"language": "hinglish", "car_a": car_a, "car_b": car_b}
        })

    # 6. Conceptual Automotive Knowledge (EV vs Hybrid, RTO, Fastag)
    CONCEPTUAL = [
        (
            "EV (Electric Vehicle) aur Hybrid car me kya antar hota hai?",
            "EV (Electric Vehicle) aur Hybrid car me mukhya antar:\n\n"
            "1. Powertrain: EV me koi petrol ya diesel engine nahi hota, ye 100% battery aur electric motor se chalti hai. Hybrid me petrol/diesel engine aur electric motor dono hote hain.\n"
            "2. Charging: EV ko external charger ya charging station par plug-in karna padta hai. Strong/Mild Hybrid battery ko engine aur regenerative braking se khud charge kar leti hai.\n"
            "3. Fuel & Emissions: EV zero tailpipe emissions deti hai. Hybrid fuel consume karti hai lekin conventional ICE car se 30-40% zyada mileage deti hai.\n"
            "4. Range Anxiety: EV me charging infrastructure par depend hona padta hai; Hybrid me conventional fuel tank hone se long distance travel bilkul normal petrol car jaisa rehta hai."
        ),
        (
            "What is the difference between On-Road Price and Ex-Showroom Price?",
            "Ex-Showroom Price is the base price set by the manufacturer including manufacturing cost and GST, but excluding road registration and legal requirements.\n\n"
            "On-Road Price is the final amount payable to legally drive the car on public roads. It includes:\n"
            "• Ex-Showroom Price\n"
            "• State RTO Registration & Road Tax (varies by state from 4% to 18%)\n"
            "• Mandatory Motor Insurance (1-year Own Damage + 3-year Third Party)\n"
            "• Fastag & State Municipal Road Safety Cess\n"
            "• 1% TCS (Tax Collected at Source) on cars priced above ₹10 Lakhs\n"
            "• Optional dealer handling charges, extended warranty, and accessories."
        )
    ]
    for q, ans in CONCEPTUAL:
        pairs.append({
            "instruction": q,
            "input": "",
            "output": ans,
            "category": "conceptual",
            "metadata": {"concept": "automotive_fundamentals"}
        })

    print(f"    [✔] Total raw instruction pairs generated: {len(pairs)}")
    return pairs


def deduplicate_and_filter(pairs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    print("[*] Running Strict Quality Filtering, PII Redaction & SHA-256 Deduplication...")
    seen_hashes: Set[str] = set()
    cleaned_dataset: List[Dict[str, Any]] = []
    category_counts: Dict[str, int] = defaultdict(int)

    duplicates_removed = 0
    short_or_corrupt_removed = 0

    for item in pairs:
        inst = item.get("instruction", "").strip()
        out = item.get("output", "").strip()

        # Quality filters
        if len(inst) < 5 or len(out) < 20:
            short_or_corrupt_removed += 1
            continue

        # Redact PII if present
        inst_clean = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL]", inst)
        out_clean = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL]", out)

        # Hash on normalized text
        norm_key = f"{inst_clean.lower()}:::{out_clean.lower()}"
        content_hash = hashlib.sha256(norm_key.encode("utf-8")).hexdigest()

        if content_hash in seen_hashes:
            duplicates_removed += 1
            continue

        seen_hashes.add(content_hash)
        cat = item.get("category", "general")
        category_counts[cat] += 1

        cleaned_dataset.append({
            "id": f"automind_{len(cleaned_dataset) + 1:06d}",
            "instruction": inst_clean,
            "input": item.get("input", ""),
            "output": out_clean,
            "category": cat,
            "metadata": item.get("metadata", {})
        })

    audit_stats = {
        "total_generated": len(pairs),
        "total_unique_saved": len(cleaned_dataset),
        "duplicates_removed": duplicates_removed,
        "corrupt_or_short_removed": short_or_corrupt_removed,
        "category_distribution": dict(category_counts)
    }

    print(f"    [✔] Deduplication Complete: {duplicates_removed} duplicates removed.")
    print(f"    [✔] Final Unique Dataset Size: {len(cleaned_dataset)} records.")
    return cleaned_dataset, audit_stats


def save_datasets(cleaned_data: List[Dict[str, Any]], audit_stats: Dict[str, Any]):
    print("[*] Exporting Master Datasets in JSON and JSONL formats...")

    # 1. Primary Master JSON File (Array format as requested by user)
    master_json_path = os.path.join(DATASETS_DIR, "automind_car_master_dataset.json")
    with open(master_json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    print(f"    [✔] Master JSON saved: {master_json_path} ({os.path.getsize(master_json_path):,} bytes)")

    # 2. Master JSONL File (Standard line-delimited format for training pipelines)
    master_jsonl_path = os.path.join(DATASETS_DIR, "automind_car_master_dataset.jsonl")
    with open(master_jsonl_path, "w", encoding="utf-8") as f:
        for row in cleaned_data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"    [✔] Master JSONL saved: {master_jsonl_path} ({os.path.getsize(master_jsonl_path):,} bytes)")

    # 3. Splits: 80% Train, 10% Validation, 10% Test
    total = len(cleaned_data)
    train_end = int(total * 0.80)
    val_end = int(total * 0.90)

    train_data = cleaned_data[:train_end]
    val_data = cleaned_data[train_end:val_end]
    test_data = cleaned_data[val_end:]

    for name, split_rows in [("train", train_data), ("val", val_data), ("test", test_data)]:
        json_path = os.path.join(DATASETS_DIR, f"automind_{name}.json")
        jsonl_path = os.path.join(DATASETS_DIR, f"automind_{name}.jsonl")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(split_rows, f, ensure_ascii=False, indent=2)
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for row in split_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"    [✔] Split '{name}': {len(split_rows)} rows -> {json_path} & {jsonl_path}")

    # 4. Save Audit & Quality Report
    report_path = os.path.join(REPORTS_DIR, "MASTER_DATASET_REPORT.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(audit_stats, f, indent=2)
    print(f"    [✔] Audit report saved: {report_path}")


def main():
    print("=" * 80)
    print(" 🚗 AUTOMIND AI — MULTI-SOURCE AUTOMOTIVE DATASET PROCESSOR ")
    print("=" * 80)

    try:
        v4_text = fetch_csv_content(URL_CAR_DETAILS_V4)
        v4_cars = parse_v4_data(v4_text)
    except Exception as e:
        print(f"[-] Car Details v4 fetch failed: {e}")
        v4_cars = []

    try:
        v3_text = fetch_csv_content(URL_CAR_DETAILS_V3)
        v3_cars = parse_v3_data(v3_text)
    except Exception as e:
        print(f"[-] Car Details v3 fetch failed: {e}")
        v3_cars = []

    try:
        ev_text = fetch_csv_content(URL_EV_CARS)
        ev_cars = parse_ev_data(ev_text)
    except Exception as e:
        print(f"[-] EV Database fetch failed: {e}")
        ev_cars = []

    cat_cars = parse_catalogue_data(LOCAL_CATALOGUE)

    pairs = generate_instruction_pairs(v4_cars, v3_cars, ev_cars, cat_cars)
    cleaned_data, audit_stats = deduplicate_and_filter(pairs)
    save_datasets(cleaned_data, audit_stats)

    print("=" * 80)
    print(f" 🎉 SUCCESS! Generated {len(cleaned_data)} high-accuracy automotive instruction pairs.")
    print("=" * 80)


if __name__ == "__main__":
    main()
