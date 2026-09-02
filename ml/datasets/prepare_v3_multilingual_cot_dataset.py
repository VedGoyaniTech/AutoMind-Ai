"""
AutoMind AI — V3 Multilingual & Chain-of-Thought (CoT) Automotive Dataset Generator
Addresses V2 limitations:
1. Adds explicit <thought>...</thought> reasoning tokens for multi-step thinking.
2. Incorporates Native Gujarati (ગુજરાતી) and Hindi (हिंदी) QA pairs.
3. Covers multi-constraint recommendations, diagnostics, unreleased EVs, and hypercars.
"""

import os
import json
import hashlib
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASETS_DIR = os.path.join(BASE_DIR, "ml", "datasets")
os.makedirs(DATASETS_DIR, exist_ok=True)

# ── 1. Master Multilingual & CoT Dataset ─────────────────────────────────────
MASTER_V3_DATA = [
    # ── ENGLISH CoT PAIRS ───────────────────────────────────────────────────
    {
        "instruction": "What are the safest 7-seater family cars in India in 2025 with 5-star crash test ratings?",
        "output": "<thought>\n1. Identify category: 7-seater family cars in India.\n2. Filter criteria: 5-star crash test ratings (Bharat NCAP / Global NCAP).\n3. Match verified vehicles: Tata Safari (BNCAP 33.05/34), Mahindra XUV700 (GNCAP 5-Star), Toyota Innova Hycross (ASEAN NCAP 5-Star).\n4. Synthesize structured overview with ADAS and airbag details.\n</thought>\n\nThe safest 7-seater family cars in India with verified 5-star crash test ratings are:\n1. **Tata Safari (Bharat NCAP 5-Star):** Achieved 33.05/34 adult safety score with 7 airbags, Level 2 ADAS, and Land Rover OMEGArc architecture.\n2. **Mahindra XUV700 (Global NCAP 5-Star):** Features 7 airbags, Level 2 ADAS suite, and high-strength boron steel construction.\n3. **Toyota Innova Hycross (ASEAN NCAP 5-Star):** Features Toyota Safety Sense 3.0 (ADAS L2), 6 airbags, and a 23.24 km/l strong hybrid powertrain.\n4. **Hyundai Alcazar (2024 Facelift):** 6 airbags standard with SmartSense Level 2 ADAS.\n5. **Kia Carens:** 6 airbags standard, ESC, and all-4 disc brakes."
    },
    {
        "instruction": "Compare Tata Sierra EV vs Mahindra BE.05 electric SUV expected battery range and launch specs",
        "output": "<thought>\n1. Identify comparison entities: Tata Sierra EV and Mahindra BE.05.\n2. Analyze platforms: Tata Acti.ev+ vs Mahindra INGLO.\n3. Extract battery and range specs: 60-75 kWh LFP (500-550 km) vs 60-79 kWh BYD Blade LFP (450-500 km).\n4. Format as head-to-head Markdown comparison table.\n</thought>\n\n## ⚡ Tata Sierra EV vs Mahindra BE.05 — Next-Gen Electric SUV Comparison (2025–2026)\n\n| Specification / Metric | **Tata Sierra EV** | **Mahindra BE.05 (Born Electric)** |\n| :--- | :--- | :--- |\n| **Platform & Architecture** | Tata Acti.ev+ (Pure EV Skateboard) | Mahindra INGLO Platform (Born Electric Architecture) |\n| **Battery Capacity** | 60 kWh – 75 kWh LFP Battery Pack | 60 kWh – 79 kWh BYD Blade LFP Prismatic Cells |\n| **Expected Real Driving Range** | **500 – 550 km (ARAI Estimated)** | **450 – 500 km (WLTP Estimated)** |\n| **Motor Output & Drivetrain** | Single Motor FWD (170 PS) / Dual Motor AWD (280 PS) | Single Motor RWD (231 PS) / Dual Motor AWD (286 PS) |\n| **0–100 km/h Acceleration** | ~6.5 Seconds (AWD) | ~5.5 Seconds (Dual-Motor AWD) |\n| **DC Fast Charging (175 kW)** | 10% to 80% in ~29 minutes | 10% to 80% in ~30 minutes |\n| **Estimated Price Range** | ₹25.00 – ₹32.00 Lakh | ₹22.00 – ₹28.00 Lakh |\n| **Target Launch Window** | Early 2026 | October 2025 (Diwali 2025) |"
    },
    {
        "instruction": "My car OBD-II scanner shows error code P0420 with rattling noise under acceleration and reduced mileage. What components are failing and how to fix?",
        "output": "<thought>\n1. Diagnostic Trouble Code: P0420 (Catalyst System Efficiency Below Threshold Bank 1).\n2. Symptoms: Acoustic rattling under acceleration + reduced mileage.\n3. Root cause: Broken ceramic honeycomb substrate inside catalytic converter causing physical rattle and unmetered exhaust backpressure.\n4. Secondary components: Downstream O2 sensor (B1S2), exhaust manifold leaks, fuel trim rich burn.\n5. Formulate 4-step diagnostic protocol and estimated repair costs in INR.\n</thought>\n\n## 🛠️ AutoMind AI — Mechanical Diagnostic & OBD-II Troubleshooting Report\n\n**Primary Diagnostic Trouble Code (DTC):** `P0420 — Catalyst System Efficiency Below Threshold (Bank 1)`\n\n### 🔍 Root Cause Analysis & Failing Components\n1. **Degraded / Fractured Catalytic Converter Core:** The ceramic honeycomb substrate inside the converter has fractured (causing the rattling noise heard under acceleration).\n2. **Faulty Downstream Oxygen Sensor (O2 Sensor B1S2):** Reading oscillating 0.1V–0.9V signals mimicking catalyst failure.\n3. **Exhaust Manifold / Flex Pipe Leak:** Cold air leak upstream skews fuel trims.\n\n### 📋 Step-by-Step Diagnostic Protocol\n| Step | Target Component | Diagnostic Method | Expected vs Failing Condition |\n| :--- | :--- | :--- | :--- |\n| **1. Physical Sound Test** | Catalytic Body | Tap converter lightly with rubber mallet | Internal rattling = Broken honeycomb monolith ➔ Replace |\n| **2. Live O2 Sensor Waveform** | Downstream O2 (B1S2) | Read live graphing PID on OBD-II scanner | Expected: Flat 0.5V–0.7V. Failing: Rapid oscillation matching Upstream |\n| **3. Temperature Differential** | Inlet vs Outlet Pipes | Measure with Infrared Laser Thermometer | Outlet should be 10%–20% hotter than inlet |\n\n### 💰 Repair Cost Estimates\n- 💵 **OEM Catalytic Converter:** ₹15,000 – ₹45,000\n- 💵 **Bosch O2 Sensor Replacement:** ₹2,800 – ₹5,500"
    },
    {
        "instruction": "Koenigsegg Jesko Absolut vs Hennessey Venom F5 engine displacement, horsepower, transmission technology and aerodynamic top speed",
        "output": "<thought>\n1. Identify hypercar contenders: Koenigsegg Jesko Absolut vs Hennessey Venom F5.\n2. Retrieve powertrain metrics: 5.0L TT V8 (1600 HP E85, 9-speed LST, Cd 0.278, 531 km/h target) vs 6.6L 'Fury' TT V8 (1817 HP, 7-speed CIMA, Cd 0.39, 500 km/h target).\n3. Structure comparative engineering matrix with record times.\n</thought>\n\n## 🏎️ Koenigsegg Jesko Absolut vs Hennessey Venom F5 — Hypercar Engineering Comparison\n\n| Engineering Metric | **Koenigsegg Jesko Absolut** | **Hennessey Venom F5** |\n| :--- | :--- | :--- |\n| **Engine Displacement** | 5.0-Litre Flat-Plane Twin-Turbo V8 | 6.6-Litre 'Fury' Twin-Turbo Pushrod V8 |\n| **Peak Horsepower** | **1,600 HP (E85)** / 1,280 HP (Gasoline) | **1,817 HP (1,842 PS)** @ 8,000 RPM |\n| **Peak Torque** | 1,500 Nm @ 5,100 RPM | 1,617 Nm @ 5,000 RPM |\n| **Transmission Technology** | **9-Speed Light Speed Transmission (LST)** (7 multi-disc clutches) | **7-Speed CIMA Single-Clutch** Automated Manual |\n| **Aerodynamic Drag Coefficient** | **Cd 0.278 (Ultra-Low Drag Absolut Body)** | Cd 0.39 (Carbon fiber aero tub) |\n| **Targeted Top Speed** | **531 km/h+ (330 mph+) Projected** | **500 km/h+ (311 mph+) Targeted** |\n| **0–400–0 km/h Record** | **27.83 Seconds (World Record)** | Target <30 Seconds |"
    },

    # ── HINDI (DEVANAGARI) CoT PAIRS ─────────────────────────────────────────
    {
        "instruction": "मुझे 15 लाख के बजट में सबसे सुरक्षित और 6 एयरबैग वाली पारिवारिक कार चाहिए, कौन सी बेस्ट है?",
        "output": "<thought>\n1. User intent: 15 Lakh INR budget, safest family car, 6 airbags standard, Bharat/Global NCAP rating.\n2. Filter candidates: Tata Nexon (5-Star BNCAP, 6 Airbags), Mahindra XUV 3XO (5-Star capable, Level 2 ADAS), Hyundai Verna (5-Star GNCAP, 528L boot).\n3. Generate structured Hindi recommendation table with price and safety highlights.\n</thought>\n\n## 🛡️ Top Safest Family Cars Under ₹15 Lakh in India (5-Star NCAP & 6 Airbags Standard)\n\n₹15 लाख के बजट में **6 एयरबैग और 5-स्टार क्रैश सेफ्टी** वाली टॉप 3 पारिवारिक कारें:\n\n| Rank | Car Model & Variant | Ex-Showroom Price | Safety Rating | Airbags | Engine & Transmission | Key Family Safety & Space Highlight |\n| :---: | :--- | :--- | :---: | :---: | :--- | :--- |\n| **1** | **Tata Nexon (Smart Plus / Creative 1.2)** | ₹8.00 – ₹12.50 Lakh | **5-Star Bharat NCAP** | **6 Airbags Standard** | 1.2L Turbo Petrol (120 PS) / 6MT / 6AMT | 32.22/34 अडल्ट सेफ्टी स्कोर, 208mm ग्राउंड क्लीयरेंस, ESP स्टेबिलिटी कंट्रोल। |\n| **2** | **Mahindra XUV 3XO (AX5 / AX7 1.2)** | ₹7.79 – ₹13.49 Lakh | **5-Star Safety Capable** | **6 Airbags Standard** | 1.2L mStallion Turbo (111–131 PS) | सेगमेंट में लेवल 2 ADAS, पीछे 3 वयस्कों के लिए चौड़ा केबिन, चारों पहियों में डिस्क ब्रेक। |\n| **3** | **Hyundai Verna (EX / S / SX 1.5 MPI)** | ₹11.00 – ₹14.50 Lakh | **5-Star Global NCAP** | **6 Airbags Standard** | 1.5L NA Petrol (115 PS) / 6MT / IVT | 528 लीटर का बड़ा बूट स्पेस, लंबी दूरी के पारिवारिक सफर के लिए आरामदायक सेडान। |\n\n### 🏆 मुख्य निष्कर्ष\n- 🛡️ **सर्वश्रेष्ठ सुरक्षा और हाई ग्राउंड क्लीयरेंस:** **Tata Nexon**\n- ⚙️ **सर्वश्रेष्ठ आधुनिक तकनीक व ADAS:** **Mahindra XUV 3XO**\n- 🛋️ **पारिवारिक स्पेस और बूट स्पेस:** **Hyundai Verna**"
    },
    {
        "instruction": "टाटा नेक्सन vs हुंडई क्रेटा में क्या अंतर है? माइलेज और कीमत बताओ",
        "output": "<thought>\n1. Comparison entities: Tata Nexon (Compact SUV) vs Hyundai Creta (Mid-Size SUV).\n2. Metrics required: Price, mileage (petrol & diesel), safety, ground clearance, boot space.\n3. Synthesize comparative analysis in structured Markdown.\n</thought>\n\n## 📊 Tata Nexon vs Hyundai Creta — विस्तृत तुलना (माइलेज, कीमत और फीचर्स)\n\n| Metric / Feature | **Tata Nexon (Facelift)** | **Hyundai Creta (2024 Facelift)** |\n| :--- | :--- | :--- |\n| **Price Range** | ₹8.00 – ₹15.80 Lakh (Compact SUV) | ₹11.00 – ₹20.15 Lakh (Mid-Size SUV) |\n| **Engine Options** | 1.2L Turbo Petrol (120 PS) / 1.5L Diesel (115 PS) | 1.5L NA (115 PS) / 1.5L Turbo (160 PS) / 1.5L Diesel (116 PS) |\n| **Transmission** | 5MT, 6MT, 6AMT, 7-Speed Dual-Clutch (DCA) | 6MT, IVT (CVT), 6AT, 7-Speed DCT |\n| **ARAI Mileage** | 17.44 km/l (Petrol) / 23.23 km/l (Diesel) | 17.40 km/l (Petrol) / 21.80 km/l (Diesel) |\n| **Safety Rating** | **5-Star Bharat NCAP (Highest Ever Score)** | 5-Star NCAP Architecture + Level 2 ADAS |\n| **Standard Airbags** | 6 Airbags Standard | 6 Airbags Standard |\n| **Ground Clearance** | **208 mm** | 190 mm |\n| **Boot Space** | 382 Liters | **433 Liters (बड़ा फैमिली बूट)** |\n\n### 💡 आपके लिए कौन सी बेहतर है?\n- 🛡️ **Tata Nexon चुनें:** यदि आपका बजट ₹15 लाख के अंदर है और 5-स्टार भारत NCAP सुरक्षा तथा 208mm ग्राउंड क्लीयरेंस प्राथमिकता है।\n- 👑 **Hyundai Creta चुनें:** यदि आपको बड़ा केबिन स्पेस, लेवल 2 ADAS और स्मूथ IVT ऑटोमैटिक ट्रांसमिशन चाहिए।"
    },

    # ── GUJARATI (ગુજરાતી) CoT PAIRS ─────────────────────────────────────────
    {
        "instruction": "મને ૧૨ લાખ ના બજેટ માં સારી માઈલેજ આપતી ઓટોમેટિક ગાડી જોઈએ છે, કઈ લેવી જોઈએ?",
        "output": "<thought>\n1. User intent (Gujarati): ₹12 Lakh budget, high mileage (20+ km/l), automatic transmission, low maintenance.\n2. Filter candidates: Maruti Suzuki Dzire AGS (25.71 km/l, 5-Star NCAP), Maruti Fronx AGS (22.94 km/l, 190mm GC), Hyundai i20 IVT (20.1 km/l).\n3. Render structured recommendation table in Gujarati context.\n</thought>\n\n## 🚗 ૧૦–૧૨ લાખના બજેટમાં શ્રેષ્ઠ માઈલેજ આપતી ઓટોમેટિક ગાડીઓ (20+ km/l અને ઓછો મેન્ટેનન્સ)\n\nદૈનિક મુસાફરી માટે **20+ km/l માઈલેજ અને ઓટોમેટિક ગિયરબોક્સ** ધરાવતી ટોપ 3 ગાડીઓ:\n\n| ક્રમ | કાર મોડેલ અને વેરિઅન્ટ | અંદાજિત ઓન-રોડ કિંમત | ARAI માઈલેજ | સુરક્ષા અને એરબેગ્સ | ટ્રાન્સમિશન | મુખ્ય વિશેષતા |\n| :---: | :--- | :--- | :---: | :---: | :--- | :--- |\n| **1** | **Maruti Suzuki Dzire (ZXi Plus AGS)** | ~₹10.14 – ₹11.20 Lakh | **25.71 km/l** | **5-Star Global NCAP** + 6 Airbags | 5-Speed AGS Automatic | **5-સ્ટાર ક્રેશ સેફ્ટી**, સેગમેન્ટમાં સૌથી વધુ 25.71 km/l માઈલેજ, વાર્ષિક માત્ર ~₹3,500 સર્વિસ ખર્ચ. |\n| **2** | **Maruti Suzuki Fronx (Alpha AGS / AT)** | ~₹9.88 – ₹11.85 Lakh | **22.94 km/l** | 6 Airbags + ESP | 5-Speed AMT / 6-Speed AT | 190mm હાઈ ગ્રાઉન્ડ ક્લીયરન્સ, 360-ડિગ્રી પાર્કિંગ કેમેરા, અર્બન ક્રોસઓવર લુક. |\n| **3** | **Hyundai i20 (Sportz IVT)** | ~₹8.90 – ₹10.60 Lakh | **20.10 km/l** | 6 Airbags Standard | Smart Auto IVT (CVT) | ટ્રાફિકમાં અત્યંત સ્મૂથ ગિયર શિફ્ટિંગ, શાંત અને આરામદાયક પ્રીમિયમ કેબિન. |\n\n### 🏆 ખરીદી માટે ભલામણ\n- 💰 **મહત્તમ માઈલેજ અને ઓછો ખર્ચ:** **Maruti Suzuki Dzire** (25.71 km/l)\n- 🏙️ **ક્રોસઓવર લુક અને હાઈ ગ્રાઉન્ડ ક્લીયરન્સ:** **Maruti Fronx** (190mm GC)\n- 🛋️ **શહેરી ટ્રાફિકમાં સૌથી સ્મૂથ ડ્રાઈવ:** **Hyundai i20 IVT**"
    },
    {
        "instruction": "મહિન્દ્રા થાર vs જિમ્ની માંથી કઈ કાર ઓફ-રોડિંગ માટે શ્રેષ્ઠ છે?",
        "output": "<thought>\n1. User intent (Gujarati): Comparison between Mahindra Thar 4x4 and Maruti Suzuki Jimny 4x4 for off-roading.\n2. Key technical metrics: 4x4 systems (MLD vs ALLGRIP PRO), engine output, curb weight (1750kg vs 1200kg), approach/departure angles, water wading (650mm vs 300mm).\n3. Structure comparative analysis in Gujarati.\n</thought>\n\n## 🏔️ Mahindra Thar 4x4 vs Maruti Suzuki Jimny 4x4 — ઓફ-રોડિંગ સરખામણી\n\n| ફીચર / સ્પેસિફિકેશન | **Mahindra Thar 4x4 (LX Hard Top)** | **Maruti Suzuki Jimny 4x4 (Alpha AT)** |\n| :--- | :--- | :--- |\n| **કિંમત રેન્જ** | ₹14.30 – ₹17.60 Lakh (Ex-Showroom) | ₹12.74 – ₹14.79 Lakh (Ex-Showroom) |\n| **એન્જિન વિકલ્પો** | 2.0L ટર્બો પેટ્રોલ (152 PS) / 2.2L ડીઝલ (132 PS) | 1.5L K15B નેચરલી એસ્પિરેટેડ પેટ્રોલ (105 PS) |\n| **4x4 ટેકનોલોજી** | 4WD + **મિકેનિકલ લોકીંગ ડિફરન્સિયલ (MLD)** | **ALLGRIP PRO 4WD** વિથ લો રેન્જ ગિયર |\n| **વજન (Curb Weight)** | ~1,750 kg (ભારે અને મજબૂત બોડી) | **1,200 kg (હલકી અને ચપળ પહાડી કાર)** |\n| **ગ્રાઉન્ડ ક્લીયરન્સ / વોટર વેડિંગ** | **226 mm** / 650 mm વોટર વેડિંગ ડેપ્થ | 210 mm / 300 mm વોટર વેડિંગ ડેપ્થ |\n| **દરવાજા અને પ્રેક્ટિકાલિટી** | 3-ડોર (પાછળ બેસવા માટે મુશ્કેલ) | **5-ડોર (પરિવાર માટે સરળ પ્રવેશ)** |\n| **માઈલેજ** | 12.0 – 15.2 km/l | **16.39 – 16.94 km/l** |\n\n### 🔑 અંતિમ નિર્ણય (Verdict)\n- 🏔️ **હાર્ડકોર ઓફ-રોડિંગ અને રસ્તા પર રોફ માટે:** **Mahindra Thar 4x4** (પાવરફુલ ટોર્ક અને 650mm પાણી કાપવાની ક્ષમતા).\n- 🌲 **પહાડી સાંકડા રસ્તા, હળવી ઓફ-રોડિંગ અને ફેમિલી ઉપયોગ માટે:** **Maruti Jimny 4x4** (5 દરવાજા અને ઉત્તમ માઈલેજ)."
    }
]

def prepare_v3_suite():
    print("=" * 75)
    print(" 🚀 AUTOMIND AI — GENERATING V3 MULTILINGUAL & CoT DATASET ")
    print("=" * 75)

    # 1. Load V2 clean base dataset
    v2_master_path = os.path.join(DATASETS_DIR, "master_v2_combined_dataset.jsonl")
    records = []
    if os.path.exists(v2_master_path):
        with open(v2_master_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        print(f"  [+] Loaded {len(records)} verified records from V2 dataset.")

    # 2. Add V3 Multilingual and Chain-of-Thought records
    seen_hashes = {hashlib.md5(r.get("instruction", "").strip().lower().encode()).hexdigest() for r in records}
    v3_added = 0
    for item in MASTER_V3_DATA:
        h = hashlib.md5(item["instruction"].strip().lower().encode()).hexdigest()
        if h not in seen_hashes:
            records.append({
                "instruction": item["instruction"].strip(),
                "input": "",
                "output": item["output"].strip()
            })
            seen_hashes.add(h)
            v3_added += 1

    print(f"  [+] Ingested {v3_added} new Multilingual & Chain-of-Thought (CoT) instructions.")
    print(f"  [+] Total Master V3 Dataset size: {len(records)} clean instruction records.")

    # 3. Save Master V3 Dataset
    master_v3_path = os.path.join(DATASETS_DIR, "master_v3_combined_dataset.jsonl")
    with open(master_v3_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  [✔] Saved Master V3 Dataset → {master_v3_path}")

    # 4. Split into Train (90%) and Validation (10%)
    import random
    random.seed(42)
    random.shuffle(records)

    split_idx = int(len(records) * 0.90)
    train_data = records[:split_idx]
    val_data = records[split_idx:]

    train_v3_path = os.path.join(DATASETS_DIR, "train_v3.jsonl")
    val_v3_path = os.path.join(DATASETS_DIR, "validation_v3.jsonl")

    with open(train_v3_path, "w", encoding="utf-8") as f:
        for r in train_data:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(val_v3_path, "w", encoding="utf-8") as f:
        for r in val_data:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"  [✔] Train V3 (90%)      : {len(train_data)} records → {train_v3_path}")
    print(f"  [✔] Validation V3 (10%) : {len(val_data)} records → {val_v3_path}")
    print("=" * 75)

if __name__ == "__main__":
    prepare_v3_suite()
