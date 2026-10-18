"""
AutoMind AI — Structured Vehicle Media & Image Gallery Service
Provides curated authentic high-resolution automotive imagery categorized by Exterior and Interior,
along with dynamic Wikipedia/Wikimedia live vehicle resolution for any car in the database.
"""

from typing import Dict, Any, List, Optional
import urllib.request
import urllib.parse
import json
import re
import logging

logger = logging.getLogger(__name__)

# Cache for dynamically resolved vehicle images to avoid repeated network requests
_DYNAMIC_GALLERY_CACHE: Dict[str, Dict[str, Any]] = {}

VEHICLE_IMAGE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "creta": {
        "manufacturer": "Hyundai",
        "model": "Creta",
        "tagline": "India's Best-Selling Midsize SUV (2024 Facelift)",
        "images": [
            {
                "id": "creta-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/2/21/2024_Hyundai_Creta_1.5_MPi_SX%28O%29_%28India%29_front_view.png",
                "alt": "2024 Hyundai Creta Facelift Front Horizon LED DRLs",
                "category": "exterior",
                "caption": "2024 Creta Facelift — Parametric Black Chrome Grille & Quad-Beam LED Headlamps"
            },
            {
                "id": "creta-int-cabin",
                "url": "https://upload.wikimedia.org/wikipedia/commons/7/77/2021_Hyundai_Creta_SX%28O%29_CRDi_%28India%29_interior.jpg",
                "alt": "Hyundai Creta Dual Screen Cockpit & Steering",
                "category": "interior",
                "caption": "Dual 10.25-inch Connected Infotainment & Digital Driver Cluster with Ventilated Seats"
            }
        ]
    },
    "nexon": {
        "manufacturer": "Tata",
        "model": "Nexon",
        "tagline": "5-Star Bharat NCAP Smart Compact SUV",
        "images": [
            {
                "id": "nexon-ext-front",
                "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/25/Tata_Nexon_Blue_Dual_Tone.jpg/1280px-Tata_Nexon_Blue_Dual_Tone.jpg",
                "alt": "Tata Nexon Dual Tone Exterior",
                "category": "exterior",
                "caption": "Sequential Dynamic LED DRLs & Split Headlamp Architecture"
            },
            {
                "id": "nexon-int-cabin",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/2021_Tata_Punch_Creative_%28India%29_front_view_01.png/1280px-2021_Tata_Punch_Creative_%28India%29_front_view_01.png",
                "alt": "Tata Next-Gen Cockpit",
                "category": "interior",
                "caption": "10.25-inch High-Definition Floating Touchscreen with Two-Spoke Illuminated Logo Steering"
            }
        ]
    },
    "thar": {
        "manufacturer": "Mahindra",
        "model": "Thar",
        "tagline": "Iconic 4x4 Off-Road True SUV",
        "images": [
            {
                "id": "thar-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/5/51/Mahindra_Thar_SUV_in_%22Red_Rage%22_color_at_Ashiana_Brahmanda%2C_East_Singbhum_India_%28Ank_Kumar%2C_Infosys_limited%29_02_%28cropped%29.jpg",
                "alt": "Mahindra Thar Red Rage Front 4x4 Stance",
                "category": "exterior",
                "caption": "Muscular 4x4 Stance, 226mm Ground Clearance & 650mm Water Wading Capacity"
            }
        ]
    },
    "scorpio": {
        "manufacturer": "Mahindra",
        "model": "Scorpio-N",
        "tagline": "Big Daddy of SUVs — 5-Star Global NCAP",
        "images": [
            {
                "id": "scorpio-ext-front",
                "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b4/2024_Mahindra_Scorpio_Z8L_front.jpg/1280px-2024_Mahindra_Scorpio_Z8L_front.jpg",
                "alt": "2024 Mahindra Scorpio-N Z8L Front View",
                "category": "exterior",
                "caption": "2024 Mahindra Scorpio-N Z8L — Chrome Talon Grille, Sting DRLs & 4XPLOR Tech"
            }
        ]
    },
    "punch": {
        "manufacturer": "Tata",
        "model": "Punch",
        "tagline": "5-Star Global NCAP Micro SUV",
        "images": [
            {
                "id": "punch-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/1/1e/2021_Tata_Punch_Creative_%28India%29_front_view_01.png",
                "alt": "Tata Punch Creative Front View",
                "category": "exterior",
                "caption": "Tata Punch Creative — Bold SUV Proportions, 187mm Ground Clearance & 90-Degree Doors"
            }
        ]
    },
    "curvv": {
        "manufacturer": "Tata",
        "model": "Curvv",
        "tagline": "Futuristic Aerodynamic Coupe SUV (ICE & EV)",
        "images": [
            {
                "id": "curvv-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/1/1b/2025_Tata_Curvv_Creative%2B_S_Petrol_%28India%29_front_view.png",
                "alt": "2025 Tata Curvv Coupe SUV Front Profile",
                "category": "exterior",
                "caption": "2025 Tata Curvv — Sloping Fastback Aerodynamic Silhouette & Smart Flush Door Handles"
            }
        ]
    },
    "xuv700": {
        "manufacturer": "Mahindra",
        "model": "XUV700",
        "tagline": "Flagship 7-Seater Turbo Tech SUV with Level 2 ADAS",
        "images": [
            {
                "id": "xuv700-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/b/ba/2021_Mahindra_XUV700_2.2_AX7_%28India%29_front_view.png",
                "alt": "Mahindra XUV700 AX7 Luxury Front Profile",
                "category": "exterior",
                "caption": "Mahindra XUV700 AX7 — Dual 10.25-inch Superscreen Cockpit, 200 PS mStallion Turbo & Level 2 ADAS"
            }
        ]
    },
    "seltos": {
        "manufacturer": "Kia",
        "model": "Seltos",
        "tagline": "Feature-Packed Premium Midsize SUV",
        "images": [
            {
                "id": "seltos-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/6/6c/Kia_Seltos_SP2_PE_Snow_White_Pearl_%2817%29_%28cropped%29.jpg",
                "alt": "Kia Seltos Facelift Snow White Pearl",
                "category": "exterior",
                "caption": "Kia Seltos Facelift — Crown Jewel LED Headlamps, Star Map DRLs & Panoramic Sunroof"
            }
        ]
    },
    "brezza": {
        "manufacturer": "Maruti Suzuki",
        "model": "Brezza",
        "tagline": "India's Reliable High-Efficiency Compact SUV",
        "images": [
            {
                "id": "brezza-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/2022_Maruti_Suzuki_Brezza_ZXi%2B_%28India%29_front_view.png/1280px-2022_Maruti_Suzuki_Brezza_ZXi%2B_%28India%29_front_view.png",
                "alt": "Maruti Suzuki Brezza ZXi+ Front Profile",
                "category": "exterior",
                "caption": "Maruti Suzuki Brezza — Dual LED Projectors, Geometric Wheel Arches & 360 Camera"
            }
        ]
    },
    "fortuner": {
        "manufacturer": "Toyota",
        "model": "Fortuner",
        "tagline": "Indomitable 4x4 Ladder-Frame Full-Size SUV",
        "images": [
            {
                "id": "fortuner-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Toyota_Fortuner_India.jpg",
                "alt": "Toyota Fortuner 4x4 Front Stance in India",
                "category": "exterior",
                "caption": "Toyota Fortuner 4x4 — 2.8L Diesel (500 Nm Torque), Heavy-Duty Ladder Frame & High Resale Value"
            }
        ]
    },
    "swift": {
        "manufacturer": "Maruti Suzuki",
        "model": "Swift",
        "tagline": "Sporty 4th-Gen Hatchback with Z-Series Mileage",
        "images": [
            {
                "id": "swift-ext-front",
                "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3d/Suzuki_Swift_%282024%29_hybrid_DSC_6076.jpg/1280px-Suzuki_Swift_%282024%29_hybrid_DSC_6076.jpg",
                "alt": "2024 Maruti Suzuki Swift Front Stance",
                "category": "exterior",
                "caption": "2024 All-New Swift — Z-Series 1.2L 3-Cylinder Engine delivering 24.8+ km/l efficiency"
            }
        ]
    },
    "dzire": {
        "manufacturer": "Maruti Suzuki",
        "model": "Dzire",
        "tagline": "5-Star NCAP High-Efficiency Compact Sedan",
        "images": [
            {
                "id": "dzire-ext-front",
                "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e7/Suzuki_Dzire_II_1.2_GLX_Hybrid_Arctic_White_Pearl.jpg/1280px-Suzuki_Dzire_II_1.2_GLX_Hybrid_Arctic_White_Pearl.jpg",
                "alt": "Maruti Dzire Sleek Aerodynamic Sedan",
                "category": "exterior",
                "caption": "Maruti Suzuki Dzire — Crystal LED Headlamps, Segment-First Electric Sunroof & 5-Star Safety"
            }
        ]
    },
    "innova": {
        "manufacturer": "Toyota",
        "model": "Innova Hycross",
        "tagline": "Unrivalled 7/8-Seater Premium MPV with Strong Hybrid Power",
        "images": [
            {
                "id": "innova-ext-front",
                "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/36/Toyota_Innova_Zenix_2.0_V_%28III%29_%E2%80%93_f_22032025.jpg/1280px-Toyota_Innova_Zenix_2.0_V_%28III%29_%E2%80%93_f_22032025.jpg",
                "alt": "Toyota Innova Hycross Front Stance",
                "category": "exterior",
                "caption": "Toyota Innova Hycross — TNGA Monocoque Platform, Ottoman Lounge Seating & 21.1 km/l Strong Hybrid"
            }
        ]
    },
    "fronx": {
        "manufacturer": "Maruti Suzuki",
        "model": "Fronx",
        "tagline": "Coupe Crossover with Boosterjet Turbo Power",
        "images": [
            {
                "id": "fronx-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/2023_Maruti_Suzuki_Fronx_Alpha_%28India%29_front_view.png/1280px-2023_Maruti_Suzuki_Fronx_Alpha_%28India%29_front_view.png",
                "alt": "Maruti Suzuki Fronx Alpha Front Profile",
                "category": "exterior",
                "caption": "Maruti Suzuki Fronx Alpha — NEXWave Grille, Sloping Coupe Roof & 1.0L Boosterjet Turbo"
            }
        ]
    },
    "harrier": {
        "manufacturer": "Tata",
        "model": "Harrier",
        "tagline": "5-Star Bharat NCAP OMEGA-Arc Midsize SUV",
        "images": [
            {
                "id": "harrier-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Tata_Harrier_Dark_Edition_front_view.jpg/1280px-Tata_Harrier_Dark_Edition_front_view.jpg",
                "alt": "Tata Harrier Dark Edition Front View",
                "category": "exterior",
                "caption": "Tata Harrier — Land Rover D8 Derived OMEGA-Arc Architecture with 170 PS Kryotec Diesel"
            }
        ]
    },
    "safari": {
        "manufacturer": "Tata",
        "model": "Safari",
        "tagline": "Flagship 6/7-Seater Luxury SUV with 5-Star B-NCAP",
        "images": [
            {
                "id": "safari-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Tata_Safari_XZ%2B_Gold_Edition_%28India%29_front_view.png/1280px-Tata_Safari_XZ%2B_Gold_Edition_%28India%29_front_view.png",
                "alt": "Tata Safari Gold Edition Front View",
                "category": "exterior",
                "caption": "Tata Safari — Stepped-Roof Iconic Silhouette, Ventilated Captain Seats & Level 2 ADAS"
            }
        ]
    },
    "venue": {
        "manufacturer": "Hyundai",
        "model": "Venue",
        "tagline": "Smart Urban Compact SUV",
        "images": [
            {
                "id": "venue-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/2022_Hyundai_Venue_SX%28O%29_%28India%29_front_view.png/1280px-2022_Hyundai_Venue_SX%28O%29_%28India%29_front_view.png",
                "alt": "Hyundai Venue SX(O) Front Stance",
                "category": "exterior",
                "caption": "Hyundai Venue — Dark Chrome Parametric Grille, Connected LED Tail Lamps & Turbo DCT"
            }
        ]
    },
    "grand vitara": {
        "manufacturer": "Maruti Suzuki",
        "model": "Grand Vitara",
        "tagline": "AllGrip AWD & Strong Hybrid 27.97 km/l SUV",
        "images": [
            {
                "id": "grand-vitara-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/2022_Maruti_Suzuki_Grand_Vitara_Alpha%2B_%28India%29_front_view.png/1280px-2022_Maruti_Suzuki_Grand_Vitara_Alpha%2B_%28India%29_front_view.png",
                "alt": "Maruti Grand Vitara Alpha+ Front View",
                "category": "exterior",
                "caption": "Maruti Suzuki Grand Vitara — Crafted Futirism Design, Intelligent Electric Hybrid & AllGrip AWD"
            }
        ]
    },
    "sonet": {
        "manufacturer": "Kia",
        "model": "Sonet",
        "tagline": "Wild & Muscular Compact SUV with Level 1 ADAS",
        "images": [
            {
                "id": "sonet-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/2021_Kia_Sonet_HTX_%28India%29_front_view.png/1280px-2021_Kia_Sonet_HTX_%28India%29_front_view.png",
                "alt": "Kia Sonet HTX Front View",
                "category": "exterior",
                "caption": "Kia Sonet — Tiger Nose Grille, Star Map LED DRLs, Bose 7-Speaker Audio & Ventilated Seats"
            }
        ]
    },
    "xuv 3xo": {
        "manufacturer": "Mahindra",
        "model": "XUV 3XO",
        "tagline": "Turbocharged Compact SUV with Panoramic Skyroof",
        "images": [
            {
                "id": "xuv3xo-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Mahindra_XUV_3XO_front.jpg/1280px-Mahindra_XUV_3XO_front.jpg",
                "alt": "Mahindra XUV 3XO Front Profile",
                "category": "exterior",
                "caption": "Mahindra XUV 3XO — Segment-First Panoramic Skyroof, Level 2 ADAS & 130 PS TGDi Turbo Power"
            }
        ]
    },
    "zs ev": {
        "manufacturer": "MG Motor",
        "model": "ZS EV",
        "tagline": "Full-Size Electric SUV with 461 km Claimed Range",
        "images": [
            {
                "id": "zsev-ext-front",
                "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cf/MG_ZS_%28crossover%2C_second_generation%29_DSC_8542.jpg/1280px-MG_ZS_%28crossover%2C_second_generation%29_DSC_8542.jpg",
                "alt": "MG ZS EV Front Electric Profile",
                "category": "exterior",
                "caption": "MG ZS EV — 50.3 kWh Prismatic Battery, 176 PS Motor & 461 km ARAI Range with Level 2 ADAS"
            }
        ]
    },
    "elevate": {
        "manufacturer": "Honda",
        "model": "Elevate",
        "tagline": "Upright Classic SUV with Honda SENSING",
        "images": [
            {
                "id": "elevate-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/2023_Honda_Elevate_ZX_%28India%29_front_view.png/1280px-2023_Honda_Elevate_ZX_%28India%29_front_view.png",
                "alt": "Honda Elevate ZX Front View",
                "category": "exterior",
                "caption": "Honda Elevate — 220mm Class-Leading Ground Clearance, 1.5L i-VTEC & Honda SENSING ADAS"
            }
        ]
    },
    "kushaq": {
        "manufacturer": "Skoda",
        "model": "Kushaq",
        "tagline": "5-Star Global NCAP European Dynamics SUV",
        "images": [
            {
                "id": "kushaq-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Skoda_Kushaq_Style_%28India%29_front_view.png/1280px-Skoda_Kushaq_Style_%28India%29_front_view.png",
                "alt": "Skoda Kushaq Style Front View",
                "category": "exterior",
                "caption": "Skoda Kushaq — MQB-A0-IN Platform, 1.5L TSI EVO (150 PS) & 5-Star Adult and Child Safety"
            }
        ]
    },
    "taigun": {
        "manufacturer": "Volkswagen",
        "model": "Taigun",
        "tagline": "5-Star Global NCAP Engineered German SUV",
        "images": [
            {
                "id": "taigun-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Volkswagen_Taigun_GT_Plus_%28India%29_front_view.png/1280px-Volkswagen_Taigun_GT_Plus_%28India%29_front_view.png",
                "alt": "Volkswagen Taigun GT Plus Front View",
                "category": "exterior",
                "caption": "Volkswagen Taigun GT Plus — High-Rigidity Steel Body, Active Cylinder Tech & 7-Speed DSG"
            }
        ]
    },
    "baleno": {
        "manufacturer": "Maruti Suzuki",
        "model": "Baleno",
        "tagline": "India's Highest Selling Premium Hatchback",
        "images": [
            {
                "id": "baleno-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/2022_Maruti_Suzuki_Baleno_Alpha_%28India%29_front_view.png/1280px-2022_Maruti_Suzuki_Baleno_Alpha_%28India%29_front_view.png",
                "alt": "Maruti Suzuki Baleno Alpha Front View",
                "category": "exterior",
                "caption": "Maruti Suzuki Baleno Alpha — Head-Up Display (HUD), 360 Camera & DualJet Dual VVT Engine"
            }
        ]
    },
    "tiago": {
        "manufacturer": "Tata",
        "model": "Tiago",
        "tagline": "4-Star Global NCAP Solid Hatchback (ICE, CNG & EV)",
        "images": [
            {
                "id": "tiago-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Tata_Tiago_XZ%2B_%28India%29_front_view.png/1280px-Tata_Tiago_XZ%2B_%28India%29_front_view.png",
                "alt": "Tata Tiago XZ+ Front View",
                "category": "exterior",
                "caption": "Tata Tiago — Solid 4-Star Safety, Harman 8-Speaker Acoustics & Dual-Cylinder iCNG Tech"
            }
        ]
    },
    "altroz": {
        "manufacturer": "Tata",
        "model": "Altroz",
        "tagline": "5-Star Global NCAP Gold Standard Premium Hatchback",
        "images": [
            {
                "id": "altroz-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Tata_Altroz_front_view.jpg/1280px-Tata_Altroz_front_view.jpg",
                "alt": "Tata Altroz Front View",
                "category": "exterior",
                "caption": "Tata Altroz — ALFA-Arc Modular Architecture, 90-Degree Doors & DCA Dual-Clutch Automatic"
            }
        ]
    },
    "verna": {
        "manufacturer": "Hyundai",
        "model": "Verna",
        "tagline": "5-Star Global NCAP Fastback Turbo Sedan",
        "images": [
            {
                "id": "verna-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/2023_Hyundai_Verna_SX%28O%29_Turbo_%28India%29_front_view.png/1280px-2023_Hyundai_Verna_SX%28O%29_Turbo_%28India%29_front_view.png",
                "alt": "2023 Hyundai Verna SX(O) Turbo Front View",
                "category": "exterior",
                "caption": "Hyundai Verna Turbo — 160 PS 1.5L Turbo GDi, Horizon LED Strip & Level 2 ADAS"
            }
        ]
    },
    "city": {
        "manufacturer": "Honda",
        "model": "City",
        "tagline": "The Benchmark Executive Sedan with e:HEV Hybrid",
        "images": [
            {
                "id": "city-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/2020_Honda_City_ZX_%28India%29_front_view.png/1280px-2020_Honda_City_ZX_%28India%29_front_view.png",
                "alt": "Honda City 5th Gen Front View",
                "category": "exterior",
                "caption": "Honda City 5th Gen — 1.5L i-VTEC / e:HEV Dual Motor Hybrid (27.13 km/l) & Honda SENSING"
            }
        ]
    },
    "jimny": {
        "manufacturer": "Maruti Suzuki",
        "model": "Jimny",
        "tagline": "Agile Lightweight Mountain 4x4 Off-Roader",
        "images": [
            {
                "id": "jimny-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/2023_Suzuki_Jimny_5-door_%28South_Africa%29_front_view.png/1280px-2023_Suzuki_Jimny_5-door_%28South_Africa%29_front_view.png",
                "alt": "Maruti Jimny 5-Door 4x4 Front View",
                "category": "exterior",
                "caption": "Maruti Suzuki Jimny — ALLGRIP PRO 4WD with Low Range Transfer Case & Rigid 3-Link Axle"
            }
        ]
    },
    "hyryder": {
        "manufacturer": "Toyota",
        "model": "Urban Cruiser Hyryder",
        "tagline": "Self-Charging Strong Hybrid 27.97 km/l SUV",
        "images": [
            {
                "id": "hyryder-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Toyota_Urban_Cruiser_Hyryder_front_view.png/1280px-Toyota_Urban_Cruiser_Hyryder_front_view.png",
                "alt": "Toyota Urban Cruiser Hyryder Front View",
                "category": "exterior",
                "caption": "Toyota Urban Cruiser Hyryder — Toyota Hybrid System (THS-II), Panoramic Roof & 27.97 km/l"
            }
        ]
    },
    "carens": {
        "manufacturer": "Kia",
        "model": "Carens",
        "tagline": "Recreational 6/7-Seater Family Vehicle",
        "images": [
            {
                "id": "carens-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/2022_Kia_Carens_Luxury_Plus_%28India%29_front_view.png/1280px-2022_Kia_Carens_Luxury_Plus_%28India%29_front_view.png",
                "alt": "Kia Carens Luxury Plus Front View",
                "category": "exterior",
                "caption": "Kia Carens — One-Touch Electric Tumble Seats, 6 Airbags Standard & 160 PS Turbo Petrol"
            }
        ]
    },
    "exter": {
        "manufacturer": "Hyundai",
        "model": "Exter",
        "tagline": "Youthful Adventurous Micro SUV with Dashcam",
        "images": [
            {
                "id": "exter-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/2023_Hyundai_Exter_SX%28O%29_Connect_%28India%29_front_view.png/1280px-2023_Hyundai_Exter_SX%28O%29_Connect_%28India%29_front_view.png",
                "alt": "Hyundai Exter SX(O) Front View",
                "category": "exterior",
                "caption": "Hyundai Exter — H-Signature LED DRLs, Dual Dashcam with Front/Rear Recording & 6 Airbags"
            }
        ]
    },
    "windsor": {
        "manufacturer": "MG Motor",
        "model": "Windsor EV",
        "tagline": "Intelligent Crossover Utility Vehicle with BaaS Option",
        "images": [
            {
                "id": "windsor-ext-front",
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Baojun_Yunduo_001.jpg/1280px-Baojun_Yunduo_001.jpg",
                "alt": "MG Windsor EV Aerodynamic Profile",
                "category": "exterior",
                "caption": "MG Windsor EV — AeroGlide Design, 135-Degree Reclining Aero Lounge Seats & 38 kWh LFP Battery"
            }
        ]
    }
}

# Alias resolution mapping for brand/model keyword matching
MODEL_KEY_ALIASES: Dict[str, str] = {
    "hyundai creta": "creta",
    "creta facelift": "creta",
    "creta 2024": "creta",
    "tata nexon": "nexon",
    "nexon ev": "nexon",
    "mahindra thar": "thar",
    "thar 4x4": "thar",
    "thar roxx": "thar",
    "mahindra scorpio": "scorpio",
    "scorpio n": "scorpio",
    "scorpio-n": "scorpio",
    "scorpio classic": "scorpio",
    "tata punch": "punch",
    "punch ev": "punch",
    "tata curvv": "curvv",
    "curvv ev": "curvv",
    "mahindra xuv700": "xuv700",
    "xuv 700": "xuv700",
    "kia seltos": "seltos",
    "seltos facelift": "seltos",
    "maruti brezza": "brezza",
    "maruti suzuki brezza": "brezza",
    "toyota fortuner": "fortuner",
    "fortuner 4x4": "fortuner",
    "maruti swift": "swift",
    "maruti suzuki swift": "swift",
    "swift 2024": "swift",
    "maruti dzire": "dzire",
    "maruti suzuki dzire": "dzire",
    "dzire 2024": "dzire",
    "toyota innova": "innova",
    "innova hycross": "innova",
    "innova crysta": "innova",
    "maruti fronx": "fronx",
    "tata harrier": "harrier",
    "tata safari": "safari",
    "hyundai venue": "venue",
    "maruti grand vitara": "grand vitara",
    "grand vitara": "grand vitara",
    "kia sonet": "sonet",
    "mahindra xuv 3xo": "xuv 3xo",
    "xuv 3xo": "xuv 3xo",
    "xuv300": "xuv 3xo",
    "mg zs ev": "zs ev",
    "zs ev": "zs ev",
    "honda elevate": "elevate",
    "skoda kushaq": "kushaq",
    "volkswagen taigun": "taigun",
    "vw taigun": "taigun",
    "maruti baleno": "baleno",
    "tata tiago": "tiago",
    "tata altroz": "altroz",
    "hyundai verna": "verna",
    "honda city": "city",
    "maruti jimny": "jimny",
    "toyota hyryder": "hyryder",
    "kia carens": "carens",
    "hyundai exter": "exter",
    "mg windsor": "windsor",
    "windsor ev": "windsor"
}


def _fetch_wikipedia_car_image(search_term: str) -> Optional[Dict[str, str]]:
    """
    Dynamically queries Wikipedia REST summary or search endpoint to get the authentic lead image
    for any vehicle in the world. Returns dict with image URL, title, and description.
    """
    headers = {"User-Agent": "AutoMindAI/1.0 (Automotive Research Assistant; contact@automind.ai)"}

    # 1. Try direct page summary candidates
    clean_term = re.sub(r'[^\w\s-]', '', search_term).strip()
    candidates = [
        clean_term.replace(' ', '_'),
        f"{clean_term.replace(' ', '_')}_(car)",
        f"{clean_term.replace(' ', '_')}_(automobile)"
    ]

    for title in candidates:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode())
                orig_img = data.get("originalimage", {}).get("source")
                thumb_img = data.get("thumbnail", {}).get("source")
                img_url = orig_img or thumb_img
                if img_url and ("jpg" in img_url.lower() or "png" in img_url.lower() or "webp" in img_url.lower()):
                    return {
                        "url": img_url,
                        "title": data.get("title", clean_term),
                        "desc": data.get("description", f"{clean_term} Official Automotive Profile")
                    }
        except Exception:
            continue

    # 2. Fallback to Wikipedia search API
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_term + ' car')}&format=json&utf8=1&srlimit=1"
    req = urllib.request.Request(search_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            s_data = json.loads(resp.read().decode())
            results = s_data.get("query", {}).get("search", [])
            if results:
                first_title = results[0]["title"]
                sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(first_title)}"
                sum_req = urllib.request.Request(sum_url, headers=headers)
                with urllib.request.urlopen(sum_req, timeout=2.5) as sum_resp:
                    data = json.loads(sum_resp.read().decode())
                    orig_img = data.get("originalimage", {}).get("source")
                    thumb_img = data.get("thumbnail", {}).get("source")
                    img_url = orig_img or thumb_img
                    if img_url and ("jpg" in img_url.lower() or "png" in img_url.lower() or "webp" in img_url.lower()):
                        return {
                            "url": img_url,
                            "title": data.get("title", clean_term),
                            "desc": data.get("description", f"{clean_term} Official Profile")
                        }
    except Exception as e:
        logger.debug(f"[VehicleMedia] Dynamic Wikipedia image lookup notice: {e}")

    return None


def get_vehicle_gallery_for_query(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Scans a user query or vehicle model for matching media assets.
    If the vehicle is in the curated registry, returns authentic multi-angle imagery.
    If it's any other car in the database, dynamically queries Wikipedia and caches the gallery.
    """
    if not prompt or not prompt.strip():
        return None

    p_lower = prompt.lower().strip()

    # If it's a multi-vehicle comparison query, do not return single vehicle gallery
    if any(w in p_lower for w in [" vs ", " versus ", "compare ", "comparison ", "તુલના", "સરખામણી", "antar", "farak"]):
        return None

    # Check curated aliases first
    for alias, reg_key in MODEL_KEY_ALIASES.items():
        if re.search(r'\b' + re.escape(alias) + r'\b', p_lower):
            data = VEHICLE_IMAGE_REGISTRY[reg_key]
            return {
                "type": "vehicle_gallery",
                "vehicle": {
                    "manufacturer": data["manufacturer"],
                    "model": data["model"],
                    "tagline": data["tagline"]
                },
                "images": data["images"]
            }

    # Direct key lookup in curated registry
    for key, data in VEHICLE_IMAGE_REGISTRY.items():
        if re.search(r'\b' + re.escape(key) + r'\b', p_lower):
            return {
                "type": "vehicle_gallery",
                "vehicle": {
                    "manufacturer": data["manufacturer"],
                    "model": data["model"],
                    "tagline": data["tagline"]
                },
                "images": data["images"]
            }

    # Dynamic Lookup for ANY other car in the database
    # Extract likely vehicle tokens from prompt
    clean_p = re.sub(r'\b(?:what|is|the|price|of|in|car|suv|sedan|details|features|specs|mileage|on-road|ex-showroom|batao|kya|hai|che|chhe)\b', '', p_lower)
    clean_p = clean_p.strip()
    if len(clean_p) >= 3:
        # Check cache
        if clean_p in _DYNAMIC_GALLERY_CACHE:
            return _DYNAMIC_GALLERY_CACHE[clean_p]

        live_res = _fetch_wikipedia_car_image(clean_p)
        if live_res:
            gallery = {
                "type": "vehicle_gallery",
                "vehicle": {
                    "manufacturer": clean_p.split()[0].title() if len(clean_p.split()) > 1 else "Automotive",
                    "model": live_res.get("title", clean_p.title()),
                    "tagline": live_res.get("desc", f"Official {clean_p.title()} Profile")
                },
                "images": [
                    {
                        "id": f"{clean_p[:10]}-ext-live",
                        "url": live_res["url"],
                        "alt": f"{live_res.get('title', clean_p.title())} High Resolution View",
                        "category": "exterior",
                        "caption": f"Official Authentic Profile — {live_res.get('title', clean_p.title())}"
                    }
                ]
            }
            _DYNAMIC_GALLERY_CACHE[clean_p] = gallery
            return gallery

    return None


get_vehicle_media_gallery = get_vehicle_gallery_for_query
