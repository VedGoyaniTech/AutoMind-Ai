"""
AutoMind AI — Unified Vehicle Comparison Service
Detects comparison intent across English, Hindi, Hinglish, and Gujarati.
Extracts clean vehicle entities without conversational filler words.
Resolves models and brands against the verified automotive database with typo tolerance.
Enforces strict factual integrity:
- Clarifies brand-only queries (e.g. Rolls-Royce -> Ghost, Cullinan, Phantom, Spectre).
- Rejects unverified/unknown models without hallucination.
- Generates verified comparison tables strictly using dataset attributes.
"""

import re
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("automind.comparison")

class ResolutionStatus(str, Enum):
    EXACT_MODEL = "exact_model"
    BRAND_ONLY = "brand_only"
    NOT_FOUND = "not_found"

@dataclass
class VehicleResolution:
    status: ResolutionStatus
    raw_input: str
    cleaned_input: str
    brand_name: Optional[str] = None
    model_name: Optional[str] = None
    available_models: List[str] = field(default_factory=list)
    specs: Optional[Dict[str, Any]] = None

@dataclass
class ComparisonResult:
    success: bool
    intent_detected: bool
    candidate_a: Optional[str] = None
    candidate_b: Optional[str] = None
    resolution_a: Optional[VehicleResolution] = None
    resolution_b: Optional[VehicleResolution] = None
    response_markdown: str = ""
    clarification_status: str = ""  # "ready", "clarification_needed", "car_not_found", "invalid_query"

# Verified Master Database of Vehicle Models
VERIFIED_VEHICLE_DATABASE: Dict[str, Dict[str, Any]] = {
    "bmw 5 series": {
        "canonical_name": "BMW 5 Series (530Li M Sport LWB)",
        "brand": "BMW",
        "segment": "Executive Luxury Sedan (Long Wheelbase)",
        "price_range": "₹72.90 – ₹74.50 Lakh (Ex-Showroom)",
        "engine": "2.0L TwinPower Turbo Petrol (258 HP / 400 Nm) with 48V Mild Hybrid",
        "transmission": "8-Speed Steptronic Sport Automatic",
        "mileage": "15.7 km/l (ARAI)",
        "safety": "5-Star Euro NCAP, Level 2 ADAS, 8 Airbags",
        "key_highlights": "Class-leading 3,105 mm wheelbase, BMW Curved Display (14.9\" + 12.3\"), Bowers & Wilkins Surround Sound",
        "verdict_point": "Best for dynamic driver agility, athletic BMW handling, and class-longest rear legroom with modern curved displays."
    },
    "mercedes-benz e-class": {
        "canonical_name": "Mercedes-Benz E-Class (E 200 / E 220d LWB)",
        "brand": "Mercedes-Benz",
        "segment": "Executive Luxury Sedan (Long Wheelbase)",
        "price_range": "₹76.05 – ₹89.15 Lakh (Ex-Showroom)",
        "engine": "2.0L Turbo Petrol (204 HP / 320 Nm) / 2.0L Diesel (197 HP / 440 Nm)",
        "transmission": "9G-TRONIC 9-Speed Automatic",
        "mileage": "15.0 – 17.5 km/l (ARAI)",
        "safety": "5-Star Euro NCAP, Active Brake Assist, 8 Airbags",
        "key_highlights": "Chauffeur reclining rear seats with memory, MBUX Superscreen, plush air suspension ride",
        "verdict_point": "Best for pinnacle chauffeur comfort, opulent Mercedes prestige, and reclining rear executive seating."
    },
    "hyundai creta": {
        "canonical_name": "Hyundai Creta (2024 Facelift)",
        "brand": "Hyundai",
        "segment": "Mid-Size Family SUV",
        "price_range": "₹11.00 – ₹20.15 Lakh (Ex-Showroom)",
        "engine": "1.5L MPi Petrol (115 PS) / 1.5L CRDi Diesel (116 PS) / 1.5L Turbo GDi (160 PS)",
        "transmission": "6-Speed MT, IVT (CVT), 6-Speed AT, 7-Speed DCT",
        "mileage": "17.40 km/l (Petrol) / 21.80 km/l (Diesel) (ARAI)",
        "safety": "6 Airbags Standard Across All Variants, Level 2 ADAS Suite, ESC",
        "key_highlights": "Voice-enabled panoramic sunroof, dual 10.25-inch connected screens, ventilated front seats",
        "verdict_point": "Best for plush family ride compliance, widespread Hyundai service reach, and seamless city convenience."
    },
    "kia seltos": {
        "canonical_name": "Kia Seltos (Facelift)",
        "brand": "Kia",
        "segment": "Mid-Size Sporty SUV",
        "price_range": "₹10.90 – ₹20.35 Lakh (Ex-Showroom)",
        "engine": "1.5L Smartstream Petrol (115 PS) / 1.5L CRDi (116 PS) / 1.5L Turbo GDi (160 PS)",
        "transmission": "6-Speed MT, 6-Speed iMT, IVT, 6-Speed AT, 7-Speed DCT",
        "mileage": "17.00 km/l (Petrol) / 20.70 km/l (Diesel) (ARAI)",
        "safety": "6 Airbags Standard, Level 2 ADAS (17 Autonomous Features), All 4 Disc Brakes",
        "key_highlights": "Dual-zone climate control, heads-up display (HUD), aggressive GT-Line / X-Line styling",
        "verdict_point": "Best for sharp road presence, sporty handling dynamics, heads-up display, and dual-zone air conditioning."
    },
    "tata nexon": {
        "canonical_name": "Tata Nexon (Facelift)",
        "brand": "Tata",
        "segment": "Compact Sub-4m SUV",
        "price_range": "₹8.00 – ₹15.80 Lakh (Ex-Showroom)",
        "engine": "1.2L Revotron Turbo Petrol (120 PS / 170 Nm) / 1.5L Revotorq Diesel (115 PS / 260 Nm)",
        "transmission": "5-Speed MT, 6-Speed MT, 6-Speed AMT, 7-Speed DCA",
        "mileage": "17.44 km/l (Petrol) / 23.23 km/l (Diesel) (ARAI)",
        "safety": "5-Star Bharat NCAP (Highest Adult & Child Score), 6 Airbags Standard",
        "key_highlights": "Class-leading 208 mm ground clearance, 10.25-inch HD touchscreen, two-spoke illuminated steering",
        "verdict_point": "Best for top-tier 5-Star Bharat NCAP crash safety, high ground clearance, and punchy diesel efficiency."
    },
    "toyota fortuner": {
        "canonical_name": "Toyota Fortuner (4x4 / 4x2)",
        "brand": "Toyota",
        "segment": "Full-Size 7-Seater Ladder-Frame SUV",
        "price_range": "₹33.43 – ₹51.44 Lakh (Ex-Showroom)",
        "engine": "2.8L 4-Cyl Turbo Diesel (204 PS / 500 Nm) / 2.7L Petrol (166 PS / 245 Nm)",
        "transmission": "6-Speed Manual / 6-Speed Sequential Automatic with Paddle Shift",
        "mileage": "10.0 – 14.4 km/l (ARAI)",
        "safety": "7 Airbags, VSC, Hill Assist Control, 5-Star ASEAN NCAP",
        "key_highlights": "Indestructible ladder-chassis reliability, monumental resale value, high-range & low-range 4x4",
        "verdict_point": "Best for bulletproof long-term reliability, undisputed market resale value, and heavy-duty off-road durability."
    },
    "ford endeavour": {
        "canonical_name": "Ford Endeavour (Titanium+ / Sport)",
        "brand": "Ford",
        "segment": "Full-Size 7-Seater Ladder-Frame SUV",
        "price_range": "₹29.99 – ₹36.25 Lakh (Historical Ex-Showroom)",
        "engine": "2.0L EcoBlue Turbo Diesel (170 PS / 420 Nm) / 3.2L TDCi 5-Cylinder (200 PS / 470 Nm)",
        "transmission": "10-Speed SelectShift Automatic with Terrain Management",
        "mileage": "12.4 – 14.2 km/l (ARAI)",
        "safety": "7 Airbags, Semi-Autonomous Park Assist, Roll Stability Control",
        "key_highlights": "Terrain Management System, active noise cancellation cabin, supple multi-link rear suspension",
        "verdict_point": "Best for plush ride comfort, whisper-quiet cabin with active noise cancellation, and sophisticated 10-speed transmission."
    },
    "rolls-royce ghost": {
        "canonical_name": "Rolls-Royce Ghost (Series II / Extended)",
        "brand": "Rolls-Royce",
        "segment": "Ultra-Luxury Executive Saloon",
        "price_range": "₹6.95 – ₹7.95 Crore (Ex-Showroom)",
        "engine": "6.75L Twin-Turbo V12 (563 HP / 850 Nm)",
        "transmission": "8-Speed Satellite-Aided Automatic",
        "mileage": "6.3 km/l (WLTP Combined)",
        "safety": "Rolls-Royce Bespoke Safety Suite, 8 Airbags, Night Vision Assist",
        "key_highlights": "Planar suspension system, illuminated fascia, self-opening/closing doors, Magic Carpet Ride",
        "verdict_point": "Best for the finest modern chauffeur luxury, whispering V12 serenity, and handcrafted bespoke opulence."
    },
    "rolls-royce cullinan": {
        "canonical_name": "Rolls-Royce Cullinan (Series II)",
        "brand": "Rolls-Royce",
        "segment": "Ultra-Luxury All-Terrain SUV",
        "price_range": "₹6.95 – ₹7.50 Crore (Ex-Showroom)",
        "engine": "6.75L Twin-Turbo V12 (563 HP / 850 Nm)",
        "transmission": "8-Speed Automatic with Permanent All-Wheel Drive",
        "mileage": "6.6 km/l (WLTP Combined)",
        "safety": "Rolls-Royce All-Terrain Active Guard, 8 Airbags, 360 Laser Guidance",
        "key_highlights": "Viewing Suite tailgate seats, glass partition separating luggage and passenger cabin, effortless off-road mode",
        "verdict_point": "Best for commanding luxury SUV presence, all-terrain luxury travel, and bespoke tailgate viewing suites."
    },
    "rolls-royce phantom": {
        "canonical_name": "Rolls-Royce Phantom VIII (Series II)",
        "brand": "Rolls-Royce",
        "segment": "Pinnacle Ultra-Luxury Flagship Saloon",
        "price_range": "₹9.50 – ₹10.48 Crore (Ex-Showroom)",
        "engine": "6.75L Twin-Turbo V12 (563 HP / 900 Nm)",
        "transmission": "8-Speed Satellite-Aided Automatic",
        "mileage": "6.1 km/l (WLTP Combined)",
        "safety": "Pinnacle Safety Suite, Active Collision Avoidance, 8 Airbags",
        "key_highlights": "The Gallery art installation dashboard, Starlight Headliner, 130 kg sound insulation, Magic Carpet Ride",
        "verdict_point": "The ultimate automotive status symbol; uncompromised global benchmark for sovereign luxury and supreme silent ride."
    },
    "rolls-royce spectre": {
        "canonical_name": "Rolls-Royce Spectre (Electric Super Coupe)",
        "brand": "Rolls-Royce",
        "segment": "Ultra-Luxury All-Electric Super Coupe",
        "price_range": "₹7.50 Crore (Ex-Showroom)",
        "engine": "Dual Separated Electric Motors (577 HP / 900 Nm)",
        "transmission": "Single-Speed Direct Drive EV",
        "mileage": "530 km Driving Range (WLTP)",
        "safety": "Next-Gen EV Guard Suite, Level 2+ Autonomous Sensors, 8 Airbags",
        "key_highlights": "First fully electric Rolls-Royce, ultra-aerodynamic 0.25 Cd design, illuminated starlight doors",
        "verdict_point": "Best for silent zero-emissions ultra-luxury, instant electric torque, and visionary future styling."
    },
    "mahindra thar": {
        "canonical_name": "Mahindra Thar 4x4 (Hard Top)",
        "brand": "Mahindra",
        "segment": "Lifestyle 4x4 Off-Road SUV",
        "price_range": "₹14.30 – ₹17.60 Lakh (Ex-Showroom)",
        "engine": "2.0L mStallion Turbo Petrol (152 PS / 300 Nm) / 2.2L mHawk Diesel (132 PS / 300 Nm)",
        "transmission": "6-Speed Manual / 6-Speed Torque Converter Automatic",
        "mileage": "12.0 – 15.2 km/l (ARAI)",
        "safety": "4-Star Global NCAP, ESP with Roll-over Mitigation, Dual Airbags",
        "key_highlights": "Mechanical Locking Rear Differential (MLD), 226 mm ground clearance, 650 mm water wading depth",
        "verdict_point": "Best for extreme off-road trails, high water wading, rock crawling, and imposing muscular road stance."
    },
    "maruti suzuki jimny": {
        "canonical_name": "Maruti Suzuki Jimny 4x4 (5-Door)",
        "brand": "Maruti Suzuki",
        "segment": "Compact Lightweight 4x4 Off-Roader",
        "price_range": "₹12.74 – ₹14.79 Lakh (Ex-Showroom)",
        "engine": "1.5L K15B Naturally Aspirated Petrol (105 PS / 134 Nm)",
        "transmission": "5-Speed Manual / 4-Speed Automatic",
        "mileage": "16.39 – 16.94 km/l (ARAI)",
        "safety": "6 Airbags Standard, Brake Limited Slip Differential, Hill Descent Control",
        "key_highlights": "ALLGRIP PRO 4WD with low-range transfer gear, lightweight 1,200 kg agility, 5-door family usability",
        "verdict_point": "Best for tight mountain trails, sand and snow agility, city practicality, and superior fuel efficiency."
    },
    "tata nexon ev": {
        "canonical_name": "Tata Nexon EV",
        "brand": "Tata",
        "segment": "All-Electric Compact SUV",
        "price_range": "₹14.49 – ₹19.49 Lakh (Ex-Showroom)",
        "engine": "Permanent Magnet Synchronous Motor (145 PS / 215 Nm, 40.5 kWh LFP Battery)",
        "transmission": "Single-Speed Automatic EV Drive",
        "mileage": "465 km Claimed ARAI Range (~320 km Real-World)",
        "safety": "5-Star Bharat NCAP Crash Rating, 6 Airbags Standard, ESP",
        "key_highlights": "V2V and V2L appliance power bank charging, multi-mode paddle regen, 12.3-inch Cinematic touchscreen",
        "verdict_point": "Best for class-leading safety rating, V2L vehicle-to-load appliance powering, and mature nationwide charging support."
    },
    "mahindra xuv400": {
        "canonical_name": "Mahindra XUV400 EV",
        "brand": "Mahindra",
        "segment": "All-Electric Compact SUV",
        "price_range": "₹15.49 – ₹19.39 Lakh (Ex-Showroom)",
        "engine": "Electric Motor (150 PS / 310 Nm, 39.4 kWh Prismatic Battery)",
        "transmission": "Single-Speed Automatic EV Drive",
        "mileage": "456 km Claimed Range (~310 km Real-World)",
        "safety": "High-Strength Steel Platform, 6 Airbags, All 4 Disc Brakes",
        "key_highlights": "0–100 km/h in 8.3 seconds, larger 378L boot space, dual 10.25-inch infotainment cockpit",
        "verdict_point": "Best for rapid 310 Nm instantaneous sprint acceleration, larger boot luggage capacity, and plush suspension."
    },
    "bmw 3 series": {
        "canonical_name": "BMW 3 Series Gran Limousine (330Li)",
        "brand": "BMW",
        "segment": "Executive Luxury Sedan",
        "price_range": "₹60.60 – ₹62.00 Lakh (Ex-Showroom)",
        "engine": "2.0L TwinPower Turbo Petrol (258 HP / 400 Nm)",
        "transmission": "8-Speed Steptronic Sport Automatic",
        "mileage": "15.39 km/l (ARAI)",
        "safety": "5-Star Euro NCAP, 6 Airbags, Attentiveness Assistant",
        "key_highlights": "Extended wheelbase limousine legroom, BMW Curved Display, 0–100 in 6.2 seconds",
        "verdict_point": "Best for driver excitement combined with stretched rear executive legroom."
    },
    "mercedes-benz c-class": {
        "canonical_name": "Mercedes-Benz C-Class (C 200)",
        "brand": "Mercedes-Benz",
        "segment": "Executive Luxury Sedan",
        "price_range": "₹61.85 – ₹69.00 Lakh (Ex-Showroom)",
        "engine": "1.5L Turbo Petrol + 48V Mild Hybrid (204 HP / 300 Nm)",
        "transmission": "9G-TRONIC 9-Speed Automatic",
        "mileage": "16.9 km/l (ARAI)",
        "safety": "5-Star Euro NCAP, 7 Airbags, Active Brake Assist",
        "key_highlights": "Baby S-Class 11.9-inch portrait touchscreen, 64-colour ambient lighting, biometric fingerprint login",
        "verdict_point": "Best for cutting-edge cabin ambiance, high-tech portrait screen, and serene highway cruising."
    },
    "audi a4": {
        "canonical_name": "Audi A4 (Technology 40 TFSI)",
        "brand": "Audi",
        "segment": "Executive Luxury Sedan",
        "price_range": "₹51.85 – ₹55.00 Lakh (Ex-Showroom)",
        "engine": "2.0L 40 TFSI Turbo Petrol (204 HP / 320 Nm)",
        "transmission": "7-Speed S Tronic Dual-Clutch Automatic",
        "mileage": "17.4 km/l (ARAI)",
        "safety": "5-Star Euro NCAP, 8 Airbags, Audi Pre-Sense Basic",
        "key_highlights": "Audi Virtual Cockpit Plus, 19-speaker B&O 3D Sound, compliant everyday suspension",
        "verdict_point": "Best value-for-money entry in the German luxury sedan triumvirate with superb ride compliance."
    },
    "mahindra xuv700": {
        "canonical_name": "Mahindra XUV700 (AX7 L)",
        "brand": "Mahindra",
        "segment": "Flagship Mid-Size 7-Seater SUV",
        "price_range": "₹13.99 – ₹24.99 Lakh (Ex-Showroom)",
        "engine": "2.0L mStallion Turbo Petrol (200 PS / 380 Nm) / 2.2L mHawk Diesel (185 PS / 450 Nm)",
        "transmission": "6-Speed Manual / 6-Speed Torque Converter AT (AWD Option)",
        "mileage": "13.0 – 16.5 km/l (ARAI)",
        "safety": "5-Star Global NCAP, 7 Airbags, Level 2 ADAS Suite",
        "key_highlights": "Dual 10.25-inch integrated display, Sony 12-speaker 3D audio, smart flush door handles",
        "verdict_point": "Best for roaring 200 PS petrol horsepower, available AWD confidence, and high-tech ADAS safety."
    },
    "tata safari": {
        "canonical_name": "Tata Safari (Accomplished Plus)",
        "brand": "Tata",
        "segment": "Flagship 6/7-Seater Luxury SUV",
        "price_range": "₹15.49 – ₹26.50 Lakh (Ex-Showroom)",
        "engine": "2.0L Kryotec Turbocharged Diesel (170 PS / 350 Nm)",
        "transmission": "6-Speed Manual / 6-Speed Automatic with E-Shifter",
        "mileage": "14.5 – 16.3 km/l (ARAI)",
        "safety": "5-Star Bharat NCAP (Highest Ever Score in Adult/Child), 7 Airbags, Level 2 ADAS",
        "key_highlights": "Ventilated front & 2nd-row captain seats, Land Rover D8 derived OMEGA-Arc platform, 12.3-inch screen",
        "verdict_point": "Best for road presence, 2nd-row ventilated captain seat opulence, and class-defining 5-Star crash safety."
    },
    "koenigsegg jesko absolut": {
        "canonical_name": "Koenigsegg Jesko Absolut",
        "brand": "Koenigsegg",
        "segment": "Bespoke Hypercar (Top Speed Challenger)",
        "price_range": "~$3.40 Million USD (~₹28.5 Crore ex-factory)",
        "engine": "5.0L Flat-Plane Twin-Turbo V8 (1,600 HP on E85 / 1,280 HP on Petrol)",
        "transmission": "9-Speed Light Speed Transmission (LST, 7 multi-disc clutches)",
        "mileage": "Not available in dataset",
        "safety": "Ultra-Rigid Carbon Monocoque (65,000 Nm/degree torsional rigidity)",
        "key_highlights": "Ultra-low drag coefficient Cd 0.278, projected top speed 531 km/h+, 0–400–0 km/h in 27.83s",
        "verdict_point": "Best for track engineering technology, multi-clutch instant gear skipping, and record top-speed architecture."
    },
    "hennessey venom f5": {
        "canonical_name": "Hennessey Venom F5",
        "brand": "Hennessey",
        "segment": "Bespoke American Hypercar",
        "price_range": "~$3.00 Million USD (~₹25.0 Crore ex-factory)",
        "engine": "6.6L 'Fury' Twin-Turbo Pushrod V8 (1,817 HP / 1,617 Nm)",
        "transmission": "7-Speed CIMA Single-Clutch Automated Manual",
        "mileage": "Not available in dataset",
        "safety": "Bespoke Lightweight Carbon-Fiber Monocoque",
        "key_highlights": "1,817 HP highest-displacement pure combustion motor, lightweight 1,360 kg dry weight, targeted 500 km/h+",
        "verdict_point": "Best for raw American V8 displacement, unprecedented 1,817 horsepower combustion output, and straight-line fury."
    },
    "tata sierra ev": {
        "canonical_name": "Tata Sierra EV (Concept / Upcoming)",
        "brand": "Tata",
        "segment": "Electric Executive Lifestyle SUV",
        "price_range": "₹25.00 – ₹32.00 Lakh (Estimated)",
        "engine": "Single Motor FWD (170 PS) / Dual Motor AWD (280 PS), 60–75 kWh Battery",
        "transmission": "Single-Speed EV Transmission",
        "mileage": "500 – 550 km Claimed Range (Est.)",
        "safety": "Acti.ev+ Born Electric Platform, 6+ Airbags Standard",
        "key_highlights": "Iconic alpine curved glass rear windows, executive rear lounge seating layout",
        "verdict_point": "Best for neo-retro nostalgic executive styling and lounge cabin seating."
    },
    "mahindra be.05": {
        "canonical_name": "Mahindra BE.05 (Born Electric)",
        "brand": "Mahindra",
        "segment": "Electric Sports Coupe SUV",
        "price_range": "₹22.00 – ₹28.00 Lakh (Estimated)",
        "engine": "Single Motor RWD (231 PS) / Dual Motor AWD (286 PS), 60–79 kWh Battery",
        "transmission": "Single-Speed EV Transmission",
        "mileage": "450 – 500 km Claimed Range (Est.)",
        "safety": "Mahindra INGLO Dedicated EV Architecture, Level 2+ ADAS",
        "key_highlights": "Aero-sculpted sports coupe body, fighter jet cockpit driver enclosure, semi-active suspension",
        "verdict_point": "Best for razor-sharp sports coupe aerodynamics, driver-centric cockpit, and agile RWD balance."
    }
}

# Aliases mapping directly to exact models
MODEL_ALIASES: Dict[str, str] = {
    # BMW 5 Series
    "bmw 5": "bmw 5 series",
    "bmw 5 series": "bmw 5 series",
    "bmw 530li": "bmw 5 series",
    "5 series": "bmw 5 series",
    "530li": "bmw 5 series",
    "520d": "bmw 5 series",
    "bmw 520d": "bmw 5 series",
    "bwm 5": "bmw 5 series",

    # Mercedes-Benz E-Class
    "mercedes e-class": "mercedes-benz e-class",
    "mercedes e class": "mercedes-benz e-class",
    "mercedes-benz e-class": "mercedes-benz e-class",
    "mercedes-benz e class": "mercedes-benz e-class",
    "e-class": "mercedes-benz e-class",
    "e class": "mercedes-benz e-class",
    "e200": "mercedes-benz e-class",
    "e220d": "mercedes-benz e-class",
    "benz e class": "mercedes-benz e-class",
    "merc e class": "mercedes-benz e-class",

    # Hyundai Creta
    "creta": "hyundai creta",
    "hyundai creta": "hyundai creta",
    "क्रेटा": "hyundai creta",

    # Kia Seltos
    "seltos": "kia seltos",
    "kia seltos": "kia seltos",

    # Tata Nexon
    "nexon": "tata nexon",
    "tata nexon": "tata nexon",
    "नेक्सन": "tata nexon",

    # Toyota Fortuner
    "fortuner": "toyota fortuner",
    "toyota fortuner": "toyota fortuner",
    "ફોર્ચ્યુનર": "toyota fortuner",

    # Ford Endeavour
    "endeavour": "ford endeavour",
    "endeavor": "ford endeavour",
    "ford endeavour": "ford endeavour",
    "ford endeavor": "ford endeavour",

    # Rolls-Royce Models
    "rolls-royce ghost": "rolls-royce ghost",
    "rolls royce ghost": "rolls-royce ghost",
    "ghost": "rolls-royce ghost",
    "rr ghost": "rolls-royce ghost",

    "rolls-royce cullinan": "rolls-royce cullinan",
    "rolls royce cullinan": "rolls-royce cullinan",
    "cullinan": "rolls-royce cullinan",
    "rr cullinan": "rolls-royce cullinan",

    "rolls-royce phantom": "rolls-royce phantom",
    "rolls royce phantom": "rolls-royce phantom",
    "phantom": "rolls-royce phantom",
    "rr phantom": "rolls-royce phantom",

    "rolls-royce spectre": "rolls-royce spectre",
    "rolls royce spectre": "rolls-royce spectre",
    "spectre": "rolls-royce spectre",
    "rr spectre": "rolls-royce spectre",

    # Off-Roaders
    "thar": "mahindra thar",
    "mahindra thar": "mahindra thar",
    "थार": "mahindra thar",
    "jimny": "maruti suzuki jimny",
    "suzuki jimny": "maruti suzuki jimny",
    "maruti jimny": "maruti suzuki jimny",
    "maruti suzuki jimny": "maruti suzuki jimny",
    "जिम्नी": "maruti suzuki jimny",
    "જિમ્ની": "maruti suzuki jimny",

    # EVs
    "nexon ev": "tata nexon ev",
    "tata nexon ev": "tata nexon ev",
    "xuv400": "mahindra xuv400",
    "xuv 400": "mahindra xuv400",
    "mahindra xuv400": "mahindra xuv400",
    "sierra ev": "tata sierra ev",
    "tata sierra ev": "tata sierra ev",
    "sierra": "tata sierra ev",
    "be.05": "mahindra be.05",
    "be 05": "mahindra be.05",
    "be05": "mahindra be.05",
    "mahindra be.05": "mahindra be.05",

    # Executive
    "bmw 3": "bmw 3 series",
    "bmw 3 series": "bmw 3 series",
    "3 series": "bmw 3 series",
    "330li": "bmw 3 series",
    "mercedes c-class": "mercedes-benz c-class",
    "mercedes c class": "mercedes-benz c-class",
    "c-class": "mercedes-benz c-class",
    "c class": "mercedes-benz c-class",
    "audi a4": "audi a4",
    "a4": "audi a4",

    # Flagship 7-Seaters
    "xuv700": "mahindra xuv700",
    "xuv 700": "mahindra xuv700",
    "mahindra xuv700": "mahindra xuv700",
    "safari": "tata safari",
    "tata safari": "tata safari",

    # Hypercars
    "jesko": "koenigsegg jesko absolut",
    "jesko absolut": "koenigsegg jesko absolut",
    "koenigsegg jesko": "koenigsegg jesko absolut",
    "koenigsegg": "koenigsegg jesko absolut",
    "venom f5": "hennessey venom f5",
    "hennessey venom f5": "hennessey venom f5",
    "hennessey venom": "hennessey venom f5"
}

# Canonical Brands with their models for BRAND_ONLY clarification
BRAND_CATALOG: Dict[str, Dict[str, Any]] = {
    "rolls-royce": {
        "brand_name": "Rolls-Royce",
        "aliases": ["rolls royce", "rolls-royce", "rolls", "royce", "rolls royals", "rolls royal", "royals", "rr"],
        "models": [
            "Rolls-Royce Ghost",
            "Rolls-Royce Cullinan",
            "Rolls-Royce Phantom",
            "Rolls-Royce Spectre"
        ]
    },
    "bmw": {
        "brand_name": "BMW",
        "aliases": ["bmw", "bwm"],
        "models": [
            "BMW 3 Series",
            "BMW 5 Series",
            "BMW X1",
            "BMW X5",
            "BMW M5"
        ]
    },
    "mercedes-benz": {
        "brand_name": "Mercedes-Benz",
        "aliases": ["mercedes-benz", "mercedes benz", "mercedes", "merc", "benz"],
        "models": [
            "Mercedes-Benz C-Class",
            "Mercedes-Benz E-Class",
            "Mercedes-Benz S-Class",
            "Mercedes-Benz GLC"
        ]
    },
    "toyota": {
        "brand_name": "Toyota",
        "aliases": ["toyota"],
        "models": [
            "Toyota Fortuner",
            "Toyota Innova Hycross",
            "Toyota Urban Cruiser Hyryder",
            "Toyota Camry"
        ]
    },
    "ford": {
        "brand_name": "Ford",
        "aliases": ["ford"],
        "models": [
            "Ford Endeavour",
            "Ford EcoSport",
            "Ford Figo",
            "Ford Mustang"
        ]
    },
    "hyundai": {
        "brand_name": "Hyundai",
        "aliases": ["hyundai"],
        "models": [
            "Hyundai Creta",
            "Hyundai Venue",
            "Hyundai Verna",
            "Hyundai Tucson"
        ]
    },
    "kia": {
        "brand_name": "Kia",
        "aliases": ["kia"],
        "models": [
            "Kia Seltos",
            "Kia Sonet",
            "Kia Carens",
            "Kia EV6"
        ]
    },
    "tata": {
        "brand_name": "Tata",
        "aliases": ["tata", "tata motors"],
        "models": [
            "Tata Nexon",
            "Tata Punch",
            "Tata Harrier",
            "Tata Safari",
            "Tata Curvv"
        ]
    },
    "mahindra": {
        "brand_name": "Mahindra",
        "aliases": ["mahindra"],
        "models": [
            "Mahindra Thar",
            "Mahindra XUV700",
            "Mahindra Scorpio-N",
            "Mahindra XUV 3XO"
        ]
    },
    "maruti suzuki": {
        "brand_name": "Maruti Suzuki",
        "aliases": ["maruti suzuki", "maruti", "suzuki"],
        "models": [
            "Maruti Suzuki Brezza",
            "Maruti Suzuki Swift",
            "Maruti Suzuki Jimny",
            "Maruti Suzuki Grand Vitara"
        ]
    },
    "audi": {
        "brand_name": "Audi",
        "aliases": ["audi"],
        "models": [
            "Audi A4",
            "Audi A6",
            "Audi Q3",
            "Audi Q7"
        ]
    }
}

class VehicleComparisonService:
    """
    Production Engine for Car Comparison Intent, Entity Extraction,
    Dataset Verification, and Hallucination-Free Comparison Rendering.
    """

    COMPARISON_INTENT_PATTERN = re.compile(
        r"""(?ix)
        \b(?:
            vs\.?|versus|v/s|compare|comparison|compared\s+to|differ(?:ence)?\s+between|
            which\s+is\s+better|better\s+than|against|
            tulna|sarxamni|sarxamani|antar|farak|farq|
            taphawat|tafavat|
            me\s+se\s+konsi|mein\s+se\s+kaunsi|me\s+konsi|
            better\s+hai|achi\s+hai|acchi\s+hai|accha\s+hai|badhiya\s+hai|
            sari\s+che|sari\s+chhe|
            kro|karo|kar\s+do|karna\s+hai
        )\b|
        [તત]ુલના|સરખામણી|તફાવત|અંતર|માંથી\s*કઈ|
        तुलना|अंतर|फर्क|से\s*कौन
        """
    )

    # Lead-in filler phrases to strip from start of prompt
    PREFIX_FILLERS = re.compile(
        r"""(?ix)
        ^(?:
            please\s+|pls\s+|can\s+you\s+|i\s+want\s+to\s+|want\s+to\s+|
            show\s+me\s+|tell\s+me\s+|give\s+me\s+|details\s+of\s+|
            mujhe\s+|muze\s+|hume\s+|humko\s+|mera\s+|meri\s+|mere\s+|
            mane\s+|hu\s+|mara\s+mate\s+|
            batao\s+|dijiye\s+|
            compare\s+|comparison\s+of\s+|toulna\s+|sarxamni\s+|
            between\s+
        )+
        """
    )

    # Separators between car A and car B
    SEPARATOR_PATTERN = re.compile(
        r"""(?ix)
        \s+(?:
            vs\.?|versus|v/s|
            ke\s+against|against|
            better\s+hai\s+ya|achi\s+hai\s+ya|acchi\s+hai\s+ya|accha\s+hai\s+ya|badhiya\s+hai\s+ya|
            and\s+also|and|aur|ane|ne|ya|or|b/w|between
        )\s+
        """
    )

    # Trailing filler phrases to strip from extracted candidate names
    SUFFIX_FILLERS = re.compile(
        r"""(?ix)
        \b(?:
            ki\s+comparison\s+kro|ki\s+comparison\s+karo|ka\s+comparison\s+kro|ka\s+comparison\s+karo|
            ki\s+comparison|ka\s+comparison|ke\s+beech\s+comparison|
            no\s+comparison|ni\s+tulna|ni\s+sarxamni|sarxamni\s+karo|tulna\s+karo|
            compare\s+karo|compare\s+kro|compare\s+kar\s+do|compare\s+karna\s+hai|compare\s+karne|
            compare|comparison|
            kro|karo|kar\s+do|karna\s+hai|karne\s+hai|
            batao|bataiye|dijiye|kaho|
            me\s+se\s+konsi\s+achi\s+hai|me\s+se\s+konsi\s+better\s+hai|me\s+se\s+konsi|mein\s+se\s+kaunsi|me\s+konsi|
            better\s+hai\s+ya|better\s+hai|achi\s+hai|acchi\s+hai|accha\s+hai|badhiya\s+hai|
            sari\s+che|sari\s+chhe|
            which\s+is\s+better|which\s+one\s+is\s+better|which\s+one|
            cars?|gadi|gaadi|gadiyo|gadion|details|info
        )\b
        """
    )

    def detect_comparison_intent(self, query: str) -> bool:
        """Detect comparison intent across English, Hindi, Hinglish, and Gujarati."""
        if not query or not query.strip():
            return False
        q_lower = query.lower().strip()

        # Direct regex search for comparison markers
        if self.COMPARISON_INTENT_PATTERN.search(q_lower):
            return True

        # Check for multi-car separators like 'vs', 'aur', 'and' when two vehicle names appear
        if re.search(r'\b(?:vs|versus|v/s|against)\b', q_lower):
            return True

        return False

    def clean_candidate_name(self, candidate: str) -> str:
        """Remove conversational filler words from a single vehicle candidate string."""
        if not candidate:
            return ""

        cand = candidate.strip()
        # Iteratively strip leading fillers
        cand = self.PREFIX_FILLERS.sub("", cand).strip()

        # Iteratively strip trailing fillers
        cand = self.SUFFIX_FILLERS.sub("", cand).strip()

        # Clean extraneous punctuation and extra whitespace
        cand = re.sub(r'^[,\.\-:\s]+|[,\.\-:\s]+$', '', cand)
        cand = re.sub(r'\s+', ' ', cand)

        # One more pass to ensure clean boundary
        cand = self.PREFIX_FILLERS.sub("", cand).strip()
        cand = self.SUFFIX_FILLERS.sub("", cand).strip()
        cand = re.sub(r'^[,\.\-:\s]+|[,\.\-:\s]+$', '', cand)

        return cand

    def extract_candidates(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract two distinct vehicle entities from the query."""
        if not query:
            return None, None

        q = query.strip()
        # First clean off outer leading fillers
        cleaned_lead = self.PREFIX_FILLERS.sub("", q).strip()

        # Try splitting by separator pattern
        parts = self.SEPARATOR_PATTERN.split(cleaned_lead)
        if len(parts) >= 2:
            cand_a = self.clean_candidate_name(parts[0])
            cand_b = self.clean_candidate_name(parts[1])
            if cand_a and cand_b:
                return cand_a, cand_b

        # Fallback split for patterns like "Compare X vs Y" or "X vs Y"
        fallback_split = re.split(r'\s+(?:vs\.?|versus|v/s|against)\s+', cleaned_lead, flags=re.IGNORECASE)
        if len(fallback_split) >= 2:
            cand_a = self.clean_candidate_name(fallback_split[0])
            cand_b = self.clean_candidate_name(fallback_split[1])
            if cand_a and cand_b:
                return cand_a, cand_b

        # Fallback split for "X and Y"
        and_split = re.split(r'\s+(?:and|aur|ane)\s+', cleaned_lead, flags=re.IGNORECASE)
        if len(and_split) >= 2:
            cand_a = self.clean_candidate_name(and_split[0])
            cand_b = self.clean_candidate_name(and_split[1])
            if cand_a and cand_b:
                return cand_a, cand_b

        return None, None

    def resolve_candidate(self, candidate_str: str) -> VehicleResolution:
        """
        Resolves a candidate vehicle string against the dataset.
        Returns:
            - EXACT_MODEL with specs if a specific model is matched.
            - BRAND_ONLY with available models if only a brand is mentioned.
            - NOT_FOUND if the car is unknown.
        """
        cleaned = self.clean_candidate_name(candidate_str)
        c_lower = cleaned.lower()

        # Reject empty or trivial strings
        if len(c_lower) < 2:
            return VehicleResolution(
                status=ResolutionStatus.NOT_FOUND,
                raw_input=candidate_str,
                cleaned_input=cleaned
            )

        # Normalize common brand typo variants
        normalized_str = c_lower
        for typo, canonical in [
            ("rolls royals", "rolls-royce"),
            ("rolls royal", "rolls-royce"),
            ("bwm", "bmw"),
            ("mercedes benz", "mercedes-benz"),
            ("endeavor", "endeavour")
        ]:
            normalized_str = re.sub(r'\b' + re.escape(typo) + r'\b', canonical, normalized_str)

        # 1. Exact match in MODEL_ALIASES
        if normalized_str in MODEL_ALIASES:
            model_key = MODEL_ALIASES[normalized_str]
            if model_key in VERIFIED_VEHICLE_DATABASE:
                data = VERIFIED_VEHICLE_DATABASE[model_key]
                return VehicleResolution(
                    status=ResolutionStatus.EXACT_MODEL,
                    raw_input=candidate_str,
                    cleaned_input=cleaned,
                    brand_name=data["brand"],
                    model_name=data["canonical_name"],
                    specs=data
                )

        # Specific model token patterns for brands
        brand_model_patterns = {
            "rolls-royce": [
                (r'\b(?:ghost)\b', "rolls-royce ghost"),
                (r'\b(?:cullinan)\b', "rolls-royce cullinan"),
                (r'\b(?:phantom)\b', "rolls-royce phantom"),
                (r'\b(?:spectre)\b', "rolls-royce spectre")
            ],
            "bmw": [
                (r'\b(?:5\s*series|530li|520d|5\b)', "bmw 5 series"),
                (r'\b(?:3\s*series|330li|320d|3\b)', "bmw 3 series"),
                (r'\b(?:m5)\b', "bmw 5 series")
            ],
            "mercedes-benz": [
                (r'\b(?:e[\s-]?class|e200|e220d|e350d)\b', "mercedes-benz e-class"),
                (r'\b(?:c[\s-]?class|c200|c220d)\b', "mercedes-benz c-class")
            ],
            "toyota": [
                (r'\b(?:fortuner|4x4)\b', "toyota fortuner"),
            ],
            "ford": [
                (r'\b(?:endeavour|endeavor)\b', "ford endeavour"),
            ],
            "hyundai": [
                (r'\b(?:creta)\b', "hyundai creta"),
            ],
            "kia": [
                (r'\b(?:seltos)\b', "kia seltos"),
            ],
            "tata": [
                (r'\b(?:nexon\s*ev)\b', "tata nexon ev"),
                (r'\b(?:nexon)\b', "tata nexon"),
                (r'\b(?:sierra\s*ev|sierra)\b', "tata sierra ev"),
                (r'\b(?:safari)\b', "tata safari")
            ],
            "mahindra": [
                (r'\b(?:thar)\b', "mahindra thar"),
                (r'\b(?:xuv400|xuv\s*400)\b', "mahindra xuv400"),
                (r'\b(?:xuv700|xuv\s*700)\b', "mahindra xuv700"),
                (r'\b(?:be\.?05|be\s*05)\b', "mahindra be.05")
            ],
            "maruti suzuki": [
                (r'\b(?:jimny)\b', "maruti suzuki jimny"),
            ]
        }

        # 2. Check if a specific model pattern matches inside the candidate string
        for brand_key, patterns in brand_model_patterns.items():
            for pat, target_db_key in patterns:
                if re.search(pat, normalized_str, re.IGNORECASE):
                    data = VERIFIED_VEHICLE_DATABASE[target_db_key]
                    return VehicleResolution(
                        status=ResolutionStatus.EXACT_MODEL,
                        raw_input=candidate_str,
                        cleaned_input=cleaned,
                        brand_name=data["brand"],
                        model_name=data["canonical_name"],
                        specs=data
                    )

        # 3. Check for standalone model names in MODEL_ALIASES (whole word match)
        for alias, db_key in MODEL_ALIASES.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', normalized_str, re.IGNORECASE):
                data = VERIFIED_VEHICLE_DATABASE[db_key]
                return VehicleResolution(
                    status=ResolutionStatus.EXACT_MODEL,
                    raw_input=candidate_str,
                    cleaned_input=cleaned,
                    brand_name=data["brand"],
                    model_name=data["canonical_name"],
                    specs=data
                )

        # 4. Check BRAND_CATALOG for Brand-Only queries (e.g. "Rolls Royce", "Rolls Royals", "BMW")
        for brand_key, brand_info in BRAND_CATALOG.items():
            for b_alias in brand_info["aliases"]:
                if re.search(r'\b' + re.escape(b_alias) + r'\b', normalized_str, re.IGNORECASE):
                    return VehicleResolution(
                        status=ResolutionStatus.BRAND_ONLY,
                        raw_input=candidate_str,
                        cleaned_input=cleaned,
                        brand_name=brand_info["brand_name"],
                        available_models=brand_info["models"]
                    )

        # 5. Not found in verified dataset
        return VehicleResolution(
            status=ResolutionStatus.NOT_FOUND,
            raw_input=candidate_str,
            cleaned_input=cleaned
        )

    def _render_clarification_prompt(self, brand_res: VehicleResolution, other_res: VehicleResolution) -> str:
        """Ask user to select an exact model when only a brand is provided. Zero hallucinated tables."""
        brand_name = brand_res.brand_name or "is brand"
        options_list = "\n".join([f"{i+1}. **{m}**" for i, m in enumerate(brand_res.available_models)])
        other_name = other_res.model_name or other_res.brand_name or other_res.cleaned_input

        return (
            f"### ⚠️ Model Clarification Required\n\n"
            f"Aapne **{brand_name}** brand mention kiya hai, lekin comparison ke liye exact car model select karna zaroori hai.\n\n"
            f"Kripya niche diye gaye verified **{brand_name}** models me se ek select karein:\n"
            f"{options_list}\n\n"
            f"👉 Jaise hi aap exact model choose karenge (jaise: *\"{brand_res.available_models[0]} vs {other_name}\"*), "
            f"AutoMind AI hamare verified database se authentic head-to-head comparison generate karega."
        )

    def _render_not_found_message(self, valid_res: Optional[VehicleResolution], invalid_res: VehicleResolution) -> str:
        """Inform user about missing model without inventing specs."""
        inv_name = invalid_res.cleaned_input or invalid_res.raw_input
        valid_part = ""
        if valid_res and valid_res.status == ResolutionStatus.EXACT_MODEL:
            valid_part = f"**{valid_res.model_name}** hamare verified automotive database me maujood hai, par "

        return (
            f"### ⚠️ Vehicle Not Found in Dataset\n\n"
            f"{valid_part}**\"{inv_name}\"** hamare verified automotive dataset me available nahi hai.\n\n"
            f"AutoMind AI kisi bhi car ke false ya fabricated specifications generate nahi karta. "
            f"Kripya valid car brand aur model name provide karein (jaise: *Tata Nexon vs Hyundai Creta* ya *Toyota Fortuner vs Ford Endeavour*) "
            f"taaki hum exact, factual comparison provide kar sakein."
        )

    def _render_verified_comparison_table(self, res_a: VehicleResolution, res_b: VehicleResolution) -> str:
        """Render side-by-side comparison table strictly from dataset fields. No placeholders."""
        sa = res_a.specs or {}
        sb = res_b.specs or {}

        def get_field(specs: Dict[str, Any], field_name: str) -> str:
            val = specs.get(field_name)
            if not val or val == "":
                return "Not available in dataset"
            return str(val)

        m_a = res_a.model_name or "Model A"
        m_b = res_b.model_name or "Model B"

        out = []
        out.append(f"## 📊 Head-to-Head Comparison: {m_a} vs {m_b}\n")
        out.append(f"| Parameter / Feature | **{m_a}** | **{m_b}** |")
        out.append("| :--- | :--- | :--- |")
        out.append(f"| **Manufacturer & Brand** | {get_field(sa, 'brand')} | {get_field(sb, 'brand')} |")
        out.append(f"| **Vehicle Segment** | {get_field(sa, 'segment')} | {get_field(sb, 'segment')} |")
        out.append(f"| **Ex-Showroom Price** | {get_field(sa, 'price_range')} | {get_field(sb, 'price_range')} |")
        out.append(f"| **Engine & Powertrain** | {get_field(sa, 'engine')} | {get_field(sb, 'engine')} |")
        out.append(f"| **Transmission** | {get_field(sa, 'transmission')} | {get_field(sb, 'transmission')} |")
        out.append(f"| **Claimed Mileage / Range** | {get_field(sa, 'mileage')} | {get_field(sb, 'mileage')} |")
        out.append(f"| **Safety Rating & Airbags** | {get_field(sa, 'safety')} | {get_field(sb, 'safety')} |")
        out.append(f"| **Key Feature Highlight** | {get_field(sa, 'key_highlights')} | {get_field(sb, 'key_highlights')} |\n")

        out.append("### 🏆 Verified Buyer Selection Verdict")
        out.append(f"- 🚗 **Choose {m_a}:** {get_field(sa, 'verdict_point')}")
        out.append(f"- 🚙 **Choose {m_b}:** {get_field(sb, 'verdict_point')}")

        return "\n".join(out)

    def process_comparison(self, query: str) -> ComparisonResult:
        """
        Main entrypoint for processing any car comparison query.
        Handles intent detection, candidate extraction, dataset resolution,
        developer logging, and response generation.
        """
        is_comp = self.detect_comparison_intent(query)
        if not is_comp:
            return ComparisonResult(
                success=False,
                intent_detected=False,
                clarification_status="not_comparison"
            )

        cand_a, cand_b = self.extract_candidates(query)
        if not cand_a or not cand_b:
            logger.info(
                "Vehicle Comparison Flow Trace: raw_query='%s' | detected_intent=%s | extracted_entities=(%r, %r) | dataset_matches=(None, None) | clarification_status='invalid_query' | exact_models=(None, None)",
                query, is_comp, cand_a, cand_b
            )
            return ComparisonResult(
                success=False,
                intent_detected=True,
                clarification_status="invalid_query",
                response_markdown="Kripya do car models specify karein jinka comparison aap dekhna chahte hain (jaise ki *'BMW 5 Series vs Mercedes E-Class'* ya *'Creta vs Seltos'*)."
            )

        res_a = self.resolve_candidate(cand_a)
        res_b = self.resolve_candidate(cand_b)

        # Developer Trace Logging (Requirement 11)
        clarification_status = "ready"
        if res_a.status == ResolutionStatus.BRAND_ONLY or res_b.status == ResolutionStatus.BRAND_ONLY:
            clarification_status = "clarification_needed"
        elif res_a.status == ResolutionStatus.NOT_FOUND or res_b.status == ResolutionStatus.NOT_FOUND:
            clarification_status = "car_not_found"

        logger.info(
            "Vehicle Comparison Flow Trace: raw_query='%s' | detected_intent=%s | extracted_entities=(%r, %r) | dataset_matches=(%s, %s) | clarification_status='%s' | exact_models=(%r, %r)",
            query,
            is_comp,
            cand_a,
            cand_b,
            res_a.status.value,
            res_b.status.value,
            clarification_status,
            res_a.model_name if res_a.status == ResolutionStatus.EXACT_MODEL else None,
            res_b.model_name if res_b.status == ResolutionStatus.EXACT_MODEL else None
        )

        # Scenario 1: Brand Only clarification needed
        if res_a.status == ResolutionStatus.BRAND_ONLY:
            msg = self._render_clarification_prompt(res_a, res_b)
            return ComparisonResult(
                success=True,
                intent_detected=True,
                candidate_a=cand_a,
                candidate_b=cand_b,
                resolution_a=res_a,
                resolution_b=res_b,
                response_markdown=msg,
                clarification_status="clarification_needed"
            )
        if res_b.status == ResolutionStatus.BRAND_ONLY:
            msg = self._render_clarification_prompt(res_b, res_a)
            return ComparisonResult(
                success=True,
                intent_detected=True,
                candidate_a=cand_a,
                candidate_b=cand_b,
                resolution_a=res_a,
                resolution_b=res_b,
                response_markdown=msg,
                clarification_status="clarification_needed"
            )

        # Scenario 2: Unknown car model
        if res_a.status == ResolutionStatus.NOT_FOUND:
            msg = self._render_not_found_message(res_b if res_b.status == ResolutionStatus.EXACT_MODEL else None, res_a)
            return ComparisonResult(
                success=True,
                intent_detected=True,
                candidate_a=cand_a,
                candidate_b=cand_b,
                resolution_a=res_a,
                resolution_b=res_b,
                response_markdown=msg,
                clarification_status="car_not_found"
            )
        if res_b.status == ResolutionStatus.NOT_FOUND:
            msg = self._render_not_found_message(res_a if res_a.status == ResolutionStatus.EXACT_MODEL else None, res_b)
            return ComparisonResult(
                success=True,
                intent_detected=True,
                candidate_a=cand_a,
                candidate_b=cand_b,
                resolution_a=res_a,
                resolution_b=res_b,
                response_markdown=msg,
                clarification_status="car_not_found"
            )

        # Scenario 3: Both valid exact models
        comparison_markdown = self._render_verified_comparison_table(res_a, res_b)
        return ComparisonResult(
            success=True,
            intent_detected=True,
            candidate_a=cand_a,
            candidate_b=cand_b,
            resolution_a=res_a,
            resolution_b=res_b,
            response_markdown=comparison_markdown,
            clarification_status="ready"
        )

# Global singleton instance
comparison_service = VehicleComparisonService()
