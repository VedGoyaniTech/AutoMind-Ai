import os
import json
import urllib.request
import hashlib
import re
import random
from typing import List, Dict, Any, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASETS_DIR = os.path.join(BASE_DIR, "ml", "datasets")
os.makedirs(DATASETS_DIR, exist_ok=True)

# ── 1. Comprehensive Master Automotive QA Corpus ────────────────────────────
MASTER_AUTOMOTIVE_QA = [
    # Top Family / 7-Seater Cars
    {
        "instruction": "What are the safest 7-seater family cars in India in 2025 with 5-star crash test ratings?",
        "output": "The safest 7-seater family cars in India with verified crash test ratings are:\n1. **Tata Safari (Bharat NCAP 5-Star):** Achieved the highest adult safety score (33.05/34) and child safety score in Bharat NCAP history. Built on Land Rover's OMEGArc platform with 7 airbags, Level 2 ADAS (AEB, Adaptive Cruise Control, Blind Spot Monitoring).\n2. **Mahindra XUV700 (Global NCAP 5-Star):** Features 7 airbags, Level 2 ADAS suite, Driver Drowsiness Detection, and high-strength boron steel construction.\n3. **Toyota Innova Hycross (ASEAN NCAP 5-Star):** Built on the monocoque TNGA-C platform with Toyota Safety Sense 3.0 (TSS), 6 airbags, and a self-charging strong hybrid powertrain offering 23.24 km/l.\n4. **Hyundai Alcazar (2024 Facelift):** Offers 6 airbags standard across all variants, Hyundai SmartSense Level 2 ADAS with 70+ safety features, and all-4 disc brakes.\n5. **Kia Carens:** Comes with 6 airbags standard on all trims, Electronic Stability Control (ESC), and all-wheel disc brakes."
    },
    {
        "instruction": "Compare Tata Safari vs Mahindra XUV700 across price, engine, ADAS, and seating comfort.",
        "output": "Here is a head-to-head comparison between Tata Safari and Mahindra XUV700:\n\n| Feature / Metric | Tata Safari | Mahindra XUV700 |\n| :--- | :--- | :--- |\n| **Price Range** | ₹16.19 – ₹27.34 Lakh | ₹13.99 – ₹26.04 Lakh |\n| **Engine Options** | 2.0L Kryotec Turbo Diesel (170 PS / 350 Nm) | 2.0L mStallion Turbo Petrol (200 PS) / 2.2L mHawk Diesel (185 PS) |\n| **Transmission** | 6-Speed MT / 6-Speed AT (Torque Converter) | 6-Speed MT / 6-Speed AT + Optional AWD |\n| **Crash Safety** | 5-Star Bharat NCAP (Highest Ever Score) | 5-Star Global NCAP |\n| **Airbags** | 7 Airbags | 7 Airbags |\n| **ADAS Level** | Level 2 ADAS (11 features including AEB, ACC) | Level 2 ADAS (Smart Pilot Assist, Lane Keep, AEB) |\n| **3rd Row Comfort** | Dedicated AC controls & blower, spacious legroom | Good 3rd row, best for kids or medium journeys |\n\n**Verdict:** Choose **Tata Safari** if diesel road presence, supreme 2nd-row captain comfort, and top Bharat NCAP score are your priority. Choose **Mahindra XUV700** if you want high-performance turbo petrol/diesel punch, AWD capability, and a dual 10.25-inch infotainment cockpit."
    },
    {
        "instruction": "What is the price, mileage, and key specifications of the Toyota Innova Hycross Strong Hybrid?",
        "output": "The **Toyota Innova Hycross Strong Hybrid** is an executive MPV featuring a self-charging hybrid powertrain.\n\n- **Ex-Showroom Price:** ₹19.77 – ₹30.98 Lakh (India)\n- **Powertrain:** 2.0L 4-Cylinder TNGA Dual VVT-i Petrol Engine + Electric Motor paired with an e-CVT automatic transmission.\n- **Combined Power:** 186 PS (183 HP) and instant electric torque.\n- **ARAI Certified Mileage:** 23.24 km/l (real-world city mileage: ~18–21 km/l).\n- **Seating Capacity:** 7 / 8 Seater (Top ZX(O) trim gets powered Ottoman captain seats with calf support).\n- **Safety Suite:** Toyota Safety Sense 3.0 (ADAS L2 with Dynamic Radar Cruise Control, Lane Trace Assist, Pre-Collision System), 6 Airbags, 360-degree camera, and monocoque chassis."
    },
    # Electric Vehicles
    {
        "instruction": "Compare Lithium Iron Phosphate (LFP) vs Nickel Manganese Cobalt (NMC) battery chemistry in electric vehicles.",
        "output": "Here is a technical comparison of LFP vs NMC EV battery chemistries:\n\n1. **Cycle Life & Degradation:** LFP cells last 3,000+ full charge cycles (~10–15 years) with minimal degradation, whereas NMC cells typically last 1,500–2,000 cycles (~8–10 years).\n2. **Thermal Safety & Stability:** LFP is chemically stable up to 270°C and virtually immune to thermal runaway. NMC has higher energy density but requires sophisticated active liquid cooling systems to prevent overheating.\n3. **Daily Charging Habits:** LFP batteries can and should be charged to 100% daily without damaging the battery pack. NMC batteries are best maintained between 20%–80% for daily commutes to maximize longevity.\n4. **Energy Density & Weight:** NMC offers higher gravimetric energy density (200–250 Wh/kg), enabling longer range in lighter packs. LFP is heavier (140–180 Wh/kg), making it ideal for mass-market cars (e.g. Tata Nexon EV, BYD Blade Battery)."
    },
    {
        "instruction": "What are the key specs, battery size, real-world range, and price of Tata Nexon EV?",
        "output": "The **Tata Nexon EV (2024/2025 Facelift)** is India's highest-selling electric compact SUV:\n\n- **Ex-Showroom Price:** ₹14.49 – ₹19.99 Lakh (India)\n- **Battery Packs:**\n  1. *Medium Range (MR):* 30 kWh LFP battery (325 km ARAI range, ~230–250 km real world)\n  2. *Long Range (LR):* 45 kWh LFP battery (489 km ARAI range, ~350–380 km real world)\n- **Performance:** 142.7 PS power, 215 Nm instant torque (0–100 km/h in 8.9s).\n- **Charging Capabilities:** 50 kW DC Fast Charging (10%–80% in 56 minutes), 7.2 kW AC Home Wallbox (0%–100% in 6.5h).\n- **Special Tech:** Vehicle-to-Load (V2L) and Vehicle-to-Vehicle (V2V) bi-directional charging, 12.3-inch Cinematic touchscreen, 6 Airbags standard, 5-Star Bharat NCAP safety rating."
    },
    {
        "instruction": "How does Regenerative Braking work in electric cars and how does it increase driving range?",
        "output": "Regenerative braking in an electric vehicle (EV) reverses the electric motor's function during deceleration:\n1. **Energy Conversion:** When the driver lifts off the accelerator or presses the brake pedal, the electric traction motor switches into a generator. The rotational kinetic energy of the wheels spins the motor's rotor, producing AC electricity.\n2. **Inverter & Battery Storage:** The vehicle's power inverter converts this AC electricity into DC current, which is routed back into the high-voltage lithium battery pack.\n3. **Deceleration & One-Pedal Drive:** The electromagnetic resistance created by this generation slows down the car smoothly without wearing out the mechanical brake pads.\n4. **Range Extension:** In heavy urban stop-and-go traffic, multi-level regenerative braking can recover between 10% to 25% of energy, significantly extending the real-world driving range."
    },
    # Compact SUVs & Sedans
    {
        "instruction": "What is the price, mileage, and features of the Hyundai Creta 2024 facelift in India?",
        "output": "The **Hyundai Creta (2024 Facelift)** is a segment-leading compact SUV in India:\n\n- **Ex-Showroom Price Range:** ₹11.11 – ₹20.45 Lakh\n- **Engine Options:**\n  1. 1.5L Naturally Aspirated Petrol (115 PS / 144 Nm) | 6-MT / IVT (17.4 km/l)\n  2. 1.5L U2 CRDi Diesel (116 PS / 250 Nm) | 6-MT / 6-AT (21.8 km/l)\n  3. 1.5L Turbo GDi Petrol (160 PS / 253 Nm) | 7-Speed DCT (18.4 km/l)\n- **Key Features:** Dual 10.25-inch integrated infotainment & digital instrument clusters, Level 2 ADAS (19 autonomous safety features), 360-degree camera with Blind-Spot View Monitor, Voice-enabled Panoramic Sunroof, Dual-zone automatic climate control, and 6 Airbags standard across all variants."
    },
    {
        "instruction": "Compare Hyundai Verna vs Volkswagen Virtus vs Skoda Slavia in the mid-size sedan segment.",
        "output": "Here is a comparative analysis of the top mid-size sedans in India:\n\n| Parameter | Hyundai Verna (Turbo) | Volkswagen Virtus (GT) | Skoda Slavia (Monte Carlo) |\n| :--- | :--- | :--- | :--- |\n| **Price Range** | ₹11.00 – ₹17.42 Lakh | ₹11.56 – ₹19.41 Lakh | ₹12.29 – ₹19.69 Lakh |\n| **Engine** | 1.5L Turbo GDi (160 PS / 253 Nm) | 1.5L TSI EVO (150 PS / 250 Nm) | 1.5L TSI EVO (150 PS / 250 Nm) |\n| **0–100 km/h** | ~8.1 seconds (Fastest) | ~8.8 seconds | ~8.9 seconds |\n| **Crash Safety** | 5-Star Global NCAP | 5-Star Global NCAP (Highest Score) | 5-Star Global NCAP |\n| **Airbags** | 6 Airbags Standard | 6 Airbags Standard | 6 Airbags Standard |\n| **ADAS Tech** | Level 2 ADAS Suite | Not Available | Not Available |\n| **Ground Clearance** | 170 mm | 179 mm (SUV-like) | 179 mm (SUV-like) |\n| **Boot Space** | 528 Litres | 521 Litres | 521 Litres |\n\n**Verdict:** Choose **Hyundai Verna** if you want maximum straight-line power (160 PS), Level 2 ADAS tech, and high equipment level. Choose **Volkswagen Virtus / Skoda Slavia** if you prioritize solid European driving dynamics, high-speed stability, high ground clearance, and timeless aesthetic styling."
    },
    # Vintage & Classic Cars
    {
        "instruction": "What are the most famous and valuable vintage cars in automotive history and what makes them special?",
        "output": "The most legendary and valuable vintage/classic cars in automotive history include:\n1. **1962 Ferrari 250 GTO ($48.4M – $70M+):** The holy grail of collector automobiles. Powered by a 3.0L Colombo V12 producing 300 PS. Only 36 units were handcrafted by Scaglietti, dominating world GT championships.\n2. **1961 Jaguar E-Type (Series 1):** Enzo Ferrari famously described it as 'the most beautiful car ever made'. Features a 3.8L DOHC inline-6 (265 PS) capable of 150 mph (241 km/h) at a fraction of Italian exotic prices.\n3. **1963 Aston Martin DB5:** Immortalized by James Bond in 'Goldfinger'. Handcrafted with Superleggera magnesium-alloy bodywork and a 4.0L twin-cam straight-six engine (282 PS).\n4. **1954 Mercedes-Benz 300 SL Gullwing:** The world's first direct-fuel-injected production sports car with iconic roof-hinged upward opening gullwing doors and a 260 km/h top speed.\n5. **1936 Mercedes-Benz 540K Special Roadster ($10M+):** The pinnacle of pre-war luxury coachbuilding, featuring an art deco body and a 5.4L supercharged straight-8 engine.\n6. **1925 Rolls-Royce Phantom I:** The benchmark for whisper-silent royal luxury, hand-built with bespoke chassis and a 7.7L overhead-valve inline-6 engine."
    },
    # Supercars & Hypercars
    {
        "instruction": "What are the specifications, top speed, and powertrain details of the Bugatti Chiron and Ferrari SF90 Stradale?",
        "output": "Here is the technical breakdown of the Bugatti Chiron and Ferrari SF90 Stradale:\n\n### 1. Bugatti Chiron (Hypercar Benchmark)\n- **Powertrain:** 8.0-Litre Quad-Turbocharged W16 Engine\n- **Horsepower & Torque:** 1,500 PS (1,479 HP) and 1,600 Nm torque available from 2,000 to 6,000 RPM\n- **Transmission & Drivetrain:** 7-Speed Dual-Clutch Transmission with Permanent All-Wheel Drive (Haldex)\n- **Acceleration:** 0–100 km/h in 2.4s, 0–200 km/h in 6.1s\n- **Top Speed:** Electronically limited to 420 km/h (261 mph)\n- **Price:** ~₹25.00 Crore+ (International Ex-Factory / Import)\n\n### 2. Ferrari SF90 Stradale (Plug-in Hybrid Supercar)\n- **Powertrain:** 4.0-Litre Twin-Turbo V8 (780 PS) + 3 Electric Motors (220 PS)\n- **Combined Output:** 1,000 PS (986 HP) and 800 Nm torque\n- **Transmission & Drivetrain:** 8-Speed F1 Dual-Clutch Transmission with RAC-e Electric AWD\n- **Electric Only Mode (eDrive):** 25 km pure EV range on a 7.9 kWh battery\n- **Acceleration:** 0–100 km/h in 2.5s, 0–200 km/h in 6.7s\n- **Top Speed:** 340 km/h (211 mph)\n- **Price:** ₹7.50 – ₹9.00 Crore (India Ex-Showroom)"
    },
    # Technical Diagnostics & Engineering
    {
        "instruction": "Explain Dual-Clutch Transmission (DCT) vs Torque Converter (AT) vs Continuously Variable Transmission (CVT).",
        "output": "Here is a comparison of modern automatic automotive transmissions:\n\n1. **Dual-Clutch Transmission (DCT / DSG):**\n   - *How it works:* Uses two separate clutch packs (one for odd gears 1, 3, 5, 7 and one for even gears 2, 4, 6). The next gear is pre-selected.\n   - *Pros:* Lightning-fast gear shifts (<100ms), sporty feel, high fuel efficiency.\n   - *Cons:* Prone to overheating in heavy stop-and-go bumper traffic; clutch wear over time.\n\n2. **Torque Converter Automatic (AT):**\n   - *How it works:* Uses a hydraulic fluid coupling (impeller, turbine, and stator) to transfer engine torque to planetary gear sets.\n   - *Pros:* Extremely smooth, durable, exceptional reliability in city traffic, high low-end torque handling.\n   - *Cons:* Slightly higher mechanical/fluid drag than DCT.\n\n3. **Continuously Variable Transmission (CVT / e-CVT):**\n   - *How it works:* Uses a variable-diameter cone pulley system and steel belt to provide infinite gear ratios.\n   - *Pros:* Seamless continuous acceleration without shift shock, exceptional fuel economy in city commutes.\n   - *Cons:* 'Rubber-band effect' under hard throttle where engine revs before speed catches up."
    },
    {
        "instruction": "What causes white smoke vs blue smoke vs black smoke from a car exhaust pipe?",
        "output": "Exhaust smoke colors indicate specific mechanical malfunctions inside an internal combustion engine:\n\n1. **White / Grayish Thick Smoke (Coolant Leak):**\n   - *Cause:* Engine coolant is leaking into the combustion chambers, usually due to a blown head gasket, cracked engine cylinder block, or warped cylinder head.\n   - *Action:* Stop driving immediately to prevent severe engine overheating and hydraulic lock.\n\n2. **Blue / Bluish Smoke (Burning Motor Oil):**\n   - *Cause:* Engine oil is entering the cylinders and burning alongside the fuel air mixture. Commonly caused by worn piston rings, damaged valve stem oil seals, or a failing turbocharger seal.\n   - *Action:* Check engine oil levels immediately and inspect valve seals or turbo bearings.\n\n3. **Black / Dark Smoke (Excess Fuel / Rich Mixture):**\n   - *Cause:* The engine is running overly 'rich' (burning too much fuel with insufficient air). Caused by clogged air filters, malfunctioning Mass Air Flow (MAF) sensors, leaking fuel injectors, or a bad oxygen sensor.\n   - *Action:* Replace air filter, test fuel injectors, and scan OBD-II trouble codes."
    }
]

# ── 2. Helper to fetch Hugging Face dataset rows ──────────────────────────────
def fetch_hf_rows(dataset_name: str, max_pages: int = 5) -> List[Dict[str, Any]]:
    rows = []
    print(f"[*] Fetching rows from Hugging Face: {dataset_name}...")
    for page in range(max_pages):
        offset = page * 100
        url = f"https://datasets-server.huggingface.co/rows?dataset={dataset_name}&config=default&split=train&offset={offset}&limit=100"
        req = urllib.request.Request(url, headers={"User-Agent": "AutoMindAI/2.0"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                page_rows = [item.get("row", {}) for item in data.get("rows", [])]
                if not page_rows:
                    break
                rows.extend(page_rows)
                print(f"    Fetched page {page+1} ({len(page_rows)} rows, total {len(rows)})")
        except Exception as err:
            print(f"    [-] Stopped fetching at offset {offset}: {err}")
            break
    return rows

# ── 3. Parse and standardize into Instruction format ─────────────────────────
def standardize_hf_rows(rows: List[Dict[str, Any]], dataset_name: str) -> List[Dict[str, str]]:
    standardized = []
    for r in rows:
        instruction = ""
        output = ""

        # Case A: lucky-verma/car-dataset-llm (contains json-serialized messages)
        if "messages" in r:
            try:
                raw_msg = r["messages"]
                if isinstance(raw_msg, str):
                    msg_obj = json.loads(raw_msg)
                else:
                    msg_obj = raw_msg
                
                msgs = msg_obj.get("messages", []) if isinstance(msg_obj, dict) else msg_obj
                user_msg = next((m.get("content", "") for m in msgs if m.get("role") == "user"), "")
                asst_msg = next((m.get("content", "") for m in msgs if m.get("role") == "assistant"), "")
                
                if user_msg and asst_msg and len(user_msg) >= 15 and len(asst_msg) >= 20:
                    instruction = user_msg.strip()
                    output = asst_msg.strip()
            except Exception:
                pass

        # Case B: darkB/electric-vehicles-qa-dataset (<s>[INST] Q [/INST] A </s> format)
        elif "text" in r and "[INST]" in r["text"]:
            text = r["text"]
            parts = text.split("[/INST]")
            if len(parts) >= 2:
                q = parts[0].replace("<s>", "").replace("[INST]", "").strip()
                a = parts[1].replace("</s>", "").strip()
                if len(q) >= 10 and len(a) >= 15:
                    instruction = q
                    output = a

        # Case C: Generic query / answer fields
        elif "query" in r and "answer" in r:
            instruction = r["query"].strip()
            output = r["answer"].strip()

        if instruction and output:
            standardized.append({
                "instruction": instruction,
                "input": "",
                "output": output
            })
    return standardized

# ── 4. Main Data Pipeline Execution ──────────────────────────────────────────
def main():
    print("=" * 80)
    print(" AUTOMIND AI — V2 MASTER DATASET COLLECTION, CLEANING & DEDUPLICATION ")
    print("=" * 80)

    all_pairs = []

    # 1. Add Master Curated Automotive QA
    all_pairs.extend(MASTER_AUTOMOTIVE_QA)
    print(f"[+] Loaded {len(MASTER_AUTOMOTIVE_QA)} Master Automotive Instruction Pairs.")

    # 2. Fetch lucky-verma/car-dataset-llm
    lucky_rows = fetch_hf_rows("lucky-verma/car-dataset-llm", max_pages=5)
    std_lucky = standardize_hf_rows(lucky_rows, "lucky-verma/car-dataset-llm")
    all_pairs.extend(std_lucky)
    print(f"[+] Added {len(std_lucky)} valid instruction pairs from lucky-verma/car-dataset-llm.")

    # 3. Fetch darkB/electric-vehicles-qa-dataset
    darkb_rows = fetch_hf_rows("darkB/electric-vehicles-qa-dataset", max_pages=5)
    std_darkb = standardize_hf_rows(darkb_rows, "darkB/electric-vehicles-qa-dataset")
    all_pairs.extend(std_darkb)
    print(f"[+] Added {len(std_darkb)} valid instruction pairs from darkB/electric-vehicles-qa-dataset.")

    print(f"\n[*] Total Raw Combined Records: {len(all_pairs)}")

    # 4. Cleaning & MD5 Deduplication
    cleaned = []
    seen_hashes = set()
    duplicates_count = 0
    junk_count = 0

    for item in all_pairs:
        ins = item.get("instruction", "").strip()
        out = item.get("output", "").strip()

        # Reject short or non-meaningful content
        if len(ins) < 12 or len(out) < 15:
            junk_count += 1
            continue

        # Reject non-English or corrupted characters
        char_sample = ins + " " + out
        alpha_ratio = sum(1 for c in char_sample if c.isalnum() or c.isspace()) / len(char_sample)
        if alpha_ratio < 0.65:
            junk_count += 1
            continue

        # MD5 Deduplication
        content_hash = hashlib.md5(f"{ins.lower()}___{out.lower()}".encode("utf-8")).hexdigest()
        if content_hash in seen_hashes:
            duplicates_count += 1
            continue

        seen_hashes.add(content_hash)
        cleaned.append({
            "instruction": ins,
            "input": "",
            "output": out
        })

    print(f"[+] Cleaned, Verified & Deduplicated Records: {len(cleaned)}")
    print(f"[-] Duplicates Purged: {duplicates_count}")
    print(f"[-] Junk / Non-English Lines Purged: {junk_count}")

    # Shuffle with fixed seed for reproducible splits
    random.seed(42)
    random.shuffle(cleaned)

    # 5. Split into Train (85%), Validation (10%), Benchmark Test (5%)
    n_total = len(cleaned)
    n_train = int(n_total * 0.85)
    n_val = int(n_total * 0.10)
    
    train_data = cleaned[:n_train]
    val_data = cleaned[n_train:n_train + n_val]
    test_data = cleaned[n_train + n_val:]

    master_v2_file = os.path.join(DATASETS_DIR, "master_v2_combined_dataset.jsonl")
    train_v2_file = os.path.join(DATASETS_DIR, "train_v2.jsonl")
    val_v2_file = os.path.join(DATASETS_DIR, "validation_v2.jsonl")
    test_v2_file = os.path.join(DATASETS_DIR, "test_eval_v2.jsonl")

    # Save to files
    def save_jsonl(filepath: str, data_list: List[Dict[str, str]]):
        with open(filepath, "w", encoding="utf-8") as f:
            for item in data_list:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    save_jsonl(master_v2_file, cleaned)
    save_jsonl(train_v2_file, train_data)
    save_jsonl(val_v2_file, val_data)
    save_jsonl(test_v2_file, test_data)

    print("\n" + "=" * 80)
    print(" 🚀 V2 DATASET SUITE GENERATED SUCCESSFULLY")
    print("=" * 80)
    print(f"📁 Master Combined Dataset : {master_v2_file} ({len(cleaned)} rows)")
    print(f"📁 Training Set (85%)       : {train_v2_file} ({len(train_data)} rows)")
    print(f"📁 Validation Set (10%)     : {val_v2_file} ({len(val_data)} rows)")
    print(f"📁 Test Evaluation Set (5%) : {test_v2_file} ({len(test_data)} rows)")

if __name__ == "__main__":
    main()
