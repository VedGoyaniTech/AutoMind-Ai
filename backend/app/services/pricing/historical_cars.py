"""
AutoMind AI — Comprehensive Historical & Year-Wise Indian Automotive Registry (1990–2026)
Contains verified historical, luxury, vintage, classic, and modern car launches in India.
"""

from typing import Dict, Any, List, Optional

HISTORICAL_CAR_CATALOG: List[Dict[str, Any]] = [
    # --- ERA: 1990–1999 (Liberalization Era & First Premium Cars) ---
    {
        "name": "Maruti 1000 / Esteem",
        "brand": "Maruti Suzuki",
        "launch_year": 1994,
        "category": "Sedan",
        "segment": "Executive Sedan",
        "fuel_type": "petrol",
        "engine": "1.3L All-Aluminium G13BB (85 HP)",
        "price_era": "₹4.50 – ₹5.80 Lakh",
        "ex_showroom_price": 480000.0,
        "is_luxury": False,
        "is_vintage_classic": True,
        "description": "India's premier status symbol executive sedan of the 1990s."
    },
    {
        "name": "Hindustan Motors Contessa Classic",
        "brand": "Hindustan Motors",
        "launch_year": 1995,
        "category": "luxury",
        "segment": "Vintage Luxury Muscle Sedan",
        "fuel_type": "petrol",
        "engine": "1.8L Isuzu 4ZB1 Petrol (85 HP)",
        "price_era": "₹5.20 – ₹6.50 Lakh",
        "ex_showroom_price": 550000.0,
        "is_luxury": True,
        "is_vintage_classic": True,
        "description": "The quintessential Indian muscle luxury car with American styling, plush velour upholstery, and air conditioning."
    },
    {
        "name": "Mercedes-Benz E-Class (W124 Series)",
        "brand": "Mercedes-Benz",
        "launch_year": 1995,
        "category": "luxury",
        "segment": "Flagship Luxury Sedan",
        "fuel_type": "petrol",
        "engine": "E220 2.2L 4-Cyl (150 HP) / E250 Diesel",
        "price_era": "₹22.00 – ₹28.00 Lakh",
        "ex_showroom_price": 2400000.0,
        "is_luxury": True,
        "is_vintage_classic": True,
        "description": "First official Mercedes-Benz assembled in India at Telco/Tata Pune plant; the legendary 'over-engineered' luxury sedan."
    },
    {
        "name": "Tata Sierra",
        "brand": "Tata Motors",
        "launch_year": 1991,
        "category": "suv",
        "segment": "Lifestyle 3-Door SUV",
        "fuel_type": "diesel",
        "engine": "2.0L Turbo Diesel (89 HP)",
        "price_era": "₹5.00 – ₹6.20 Lakh",
        "ex_showroom_price": 520000.0,
        "is_luxury": False,
        "is_vintage_classic": True,
        "description": "India's first indigenous lifestyle SUV featuring distinctive alpine rear curved windows."
    },
    {
        "name": "Tata Safari 4x4",
        "brand": "Tata Motors",
        "launch_year": 1998,
        "category": "suv",
        "segment": "Full-size 4x4 SUV",
        "fuel_type": "diesel",
        "engine": "2.0L Turbo Diesel (90 HP)",
        "price_era": "₹8.25 – ₹9.75 Lakh",
        "ex_showroom_price": 850000.0,
        "is_luxury": True,
        "is_vintage_classic": True,
        "description": "India's first indigenous full-size luxury SUV with 4x4 shift-on-the-fly and legendary road presence."
    },
    {
        "name": "Honda City 1.3 / 1.5 (Type 1)",
        "brand": "Honda",
        "launch_year": 1998,
        "category": "Sedan",
        "segment": "Premium Sedan",
        "fuel_type": "petrol",
        "engine": "1.5L Hyper 16-Valve (100 HP)",
        "price_era": "₹6.80 – ₹7.90 Lakh",
        "ex_showroom_price": 720000.0,
        "is_luxury": False,
        "is_vintage_classic": True,
        "description": "Introduced Japanese precision, free-revving petrol performance, and premium interior refinement to India."
    },

    # --- YEAR 2000 LAUNCHES (Millennium Luxury, Sports & Vintage Classics) ---
    {
        "name": "Mercedes-Benz E-Class (W210 'Bug-Eye')",
        "brand": "Mercedes-Benz",
        "launch_year": 2000,
        "category": "luxury",
        "segment": "Executive Luxury Sedan",
        "fuel_type": "petrol",
        "engine": "E240 2.6L V6 (170 HP) / E220 CDI (143 HP)",
        "price_era": "₹32.00 – ₹38.00 Lakh",
        "ex_showroom_price": 3500000.0,
        "is_luxury": True,
        "is_vintage_classic": True,
        "description": "Iconic twin-round-headlight 'Bug-Eye' luxury sedan officially assembled in Pune in 2000, bringing electronic stability and dual-zone climate control to India."
    },
    {
        "name": "Mercedes-Benz S-Class (W220)",
        "brand": "Mercedes-Benz",
        "launch_year": 2000,
        "category": "luxury",
        "segment": "Ultra-Luxury Flagship Sedan",
        "fuel_type": "petrol",
        "engine": "S320 3.2L V6 (224 HP) / S500 V8 (306 HP)",
        "price_era": "₹65.00 – ₹85.00 Lakh",
        "ex_showroom_price": 7000000.0,
        "is_luxury": True,
        "is_vintage_classic": True,
        "description": "The benchmark luxury limousine of 2000 in India, featuring Airmatic air suspension, soft-close doors, ventilated seats, and COMAND cockpit system."
    },
    {
        "name": "Honda City 1.5 VTEC (Type 2)",
        "brand": "Honda",
        "launch_year": 2000,
        "category": "Sedan",
        "segment": "Enthusiast Sports Sedan",
        "fuel_type": "petrol",
        "engine": "1.5L VTEC D15B (106 HP @ 6,800 RPM)",
        "price_era": "₹8.40 – ₹9.20 Lakh",
        "ex_showroom_price": 860000.0,
        "is_luxury": True,
        "is_vintage_classic": True,
        "description": "The Holy Grail of Indian tuner cars, launched in late 2000 with silver face dials, rear spoiler, and the legendary high-revving 1.5L VTEC engine."
    },
    {
        "name": "Mitsubishi Lancer SFXi / GLXi",
        "brand": "Mitsubishi",
        "launch_year": 2000,
        "category": "Sedan",
        "segment": "Rally-Bred Premium Sedan",
        "fuel_type": "petrol",
        "engine": "1.5L 4G15 (87 HP) / 2.0L Diesel (68 HP)",
        "price_era": "₹7.80 – ₹9.10 Lakh",
        "ex_showroom_price": 820000.0,
        "is_luxury": True,
        "is_vintage_classic": True,
        "description": "Rally Heritage premium sedan with iconic rear spoiler, multi-link rear suspension, and Italian leather seats."
    },
    {
        "name": "Ford Ikon 1.6 Rocam 'The Josh Machine'",
        "brand": "Ford",
        "launch_year": 2000,
        "category": "Sedan",
        "segment": "Sporty Midsize Sedan",
        "fuel_type": "petrol",
        "engine": "1.6L Rocam SOHC (92 HP / 130 Nm)",
        "price_era": "₹5.90 – ₹6.80 Lakh",
        "ex_showroom_price": 620000.0,
        "is_luxury": False,
        "is_vintage_classic": True,
        "description": "Marketed as 'The Josh Machine', celebrated for its hydraulic steering feel, short-throw gearbox, and lively throttle response."
    },
    {
        "name": "Hyundai Accent GLS",
        "brand": "Hyundai",
        "launch_year": 2000,
        "category": "Sedan",
        "segment": "Family Executive Sedan",
        "fuel_type": "petrol",
        "engine": "1.5L Alpha SOHC (94 HP)",
        "price_era": "₹5.50 – ₹6.40 Lakh",
        "ex_showroom_price": 580000.0,
        "is_luxury": False,
        "is_vintage_classic": True,
        "description": "Hyundai's stylish entry luxury sedan in 2000 that competed directly with Maruti Esteem and Honda City."
    },
    {
        "name": "Toyota Qualis",
        "brand": "Toyota",
        "launch_year": 2000,
        "category": "MPV",
        "segment": "Multi-Utility Vehicle (MUV)",
        "fuel_type": "diesel",
        "engine": "2.4L 2L Diesel (75 HP / 151 Nm)",
        "price_era": "₹5.40 – ₹7.20 Lakh",
        "ex_showroom_price": 590000.0,
        "is_luxury": False,
        "is_vintage_classic": True,
        "description": "Launched in January 2000 as Toyota's debut vehicle in India; bulletproof reliability that established Toyota's reputation."
    },
    {
        "name": "Mahindra Bolero",
        "brand": "Mahindra",
        "launch_year": 2000,
        "category": "suv",
        "segment": "Rugged Utility Vehicle",
        "fuel_type": "diesel",
        "engine": "2.5L Peugeot XD3P / DI Diesel (72 HP)",
        "price_era": "₹4.80 – ₹5.60 Lakh",
        "ex_showroom_price": 495000.0,
        "is_luxury": False,
        "is_vintage_classic": True,
        "description": "Launched in August 2000, became India's longest-running best-selling rugged rural and semi-urban workhorse."
    },
    {
        "name": "Maruti Zen Classic",
        "brand": "Maruti Suzuki",
        "launch_year": 2000,
        "category": "Hatchback",
        "segment": "Retro Classic Hatchback",
        "fuel_type": "petrol",
        "engine": "1.0L All-Aluminium G10B (60 HP)",
        "price_era": "₹3.60 – ₹4.10 Lakh",
        "ex_showroom_price": 385000.0,
        "is_luxury": False,
        "is_vintage_classic": True,
        "description": "Limited-edition millennium retro design featuring round chrome headlamps, vintage mesh grille, and retro chrome bumper guards."
    },

    # --- YEAR 2001–2010 (European Invasion & Modern Luxury Boom) ---
    {
        "name": "Skoda Octavia 1.9 TDI",
        "brand": "Skoda",
        "launch_year": 2001,
        "category": "luxury",
        "segment": "European Luxury Liftback",
        "fuel_type": "diesel",
        "engine": "1.9L Turbocharged Pumpe-Düse TDI (90 HP)",
        "price_era": "₹10.50 – ₹13.00 Lakh",
        "ex_showroom_price": 1100000.0,
        "is_luxury": True,
        "is_vintage_classic": True,
        "description": "Revolutionized diesel luxury in India with vault-like German build quality, massive 528-liter boot, and phenomenal fuel economy."
    },
    {
        "name": "Honda Accord V6",
        "brand": "Honda",
        "launch_year": 2003,
        "category": "luxury",
        "segment": "Executive Luxury Sedan",
        "fuel_type": "petrol",
        "engine": "3.0L V6 VTEC (240 HP)",
        "price_era": "₹16.00 – ₹18.50 Lakh",
        "ex_showroom_price": 1650000.0,
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "India's premier executive luxury choice for corporate MDs with silken V6 power and armchair ride comfort."
    },
    {
        "name": "Toyota Fortuner 4x4",
        "brand": "Toyota",
        "launch_year": 2009,
        "category": "suv",
        "segment": "Full-Size D2 4x4 SUV",
        "fuel_type": "diesel",
        "engine": "3.0L D-4D Turbo Diesel (171 HP / 343 Nm)",
        "price_era": "₹18.45 – ₹20.00 Lakh",
        "ex_showroom_price": 1845000.0,
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "Launched in August 2009, dominated the premium full-size SUV category in India with indestructible off-road capability."
    },
    {
        "name": "BMW 3 Series (E90)",
        "brand": "BMW",
        "launch_year": 2007,
        "category": "luxury",
        "segment": "Luxury Sports Sedan",
        "fuel_type": "petrol",
        "engine": "320d 2.0L Diesel (177 HP) / 330i Inline-6 (258 HP)",
        "price_era": "₹28.00 – ₹36.00 Lakh",
        "ex_showroom_price": 3100000.0,
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "First localized BMW assembled in Chennai, offering 50:50 weight distribution and hydraulic steering precision."
    },
    {
        "name": "Audi A6 Matrix",
        "brand": "Audi",
        "launch_year": 2008,
        "category": "luxury",
        "segment": "Executive Luxury Sedan",
        "fuel_type": "diesel",
        "engine": "3.0L TDI Quattro (240 HP / 500 Nm)",
        "price_era": "₹38.00 – ₹47.00 Lakh",
        "ex_showroom_price": 4200000.0,
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "Pioneered LED daytime running lights and Quattro all-wheel drive luxury touring in India."
    }
]

def query_historical_cars(
    year: Optional[int] = None,
    is_luxury: Optional[bool] = None,
    is_vintage: Optional[bool] = None,
    fuel_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    brand_or_model: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Filters historical, recent (2018-2025) and vintage car launches based on user criteria."""
    results = []
    b_filter = (brand_or_model or "").lower().strip()
    cat_filter = (category or "").lower().strip()
    status_filter = (status or "").lower().strip()

    for car in HISTORICAL_CAR_CATALOG:
        # Year filter
        if year is not None and car["launch_year"] != year:
            continue
            
        # Luxury filter
        if is_luxury is True and not car.get("is_luxury", False):
            continue

        # Vintage / Classic filter
        if is_vintage is True and not car.get("is_vintage_classic", False):
            continue

        # Category filter (suv, sedan, hatchback, ev, mpv, luxury)
        if cat_filter:
            car_cat = car.get("category", "").lower()
            car_seg = car.get("segment", "").lower()
            if cat_filter in ["ev", "electric"]:
                if car_cat != "ev" and car.get("fuel_type", "").lower() != "electric":
                    continue
            elif cat_filter not in car_cat and cat_filter not in car_seg:
                continue

        # Status filter (launched, upcoming, facelift)
        if status_filter and car.get("status", "launched").lower() != status_filter:
            continue

        # Fuel filter
        if fuel_type and car.get("fuel_type", "").lower() != fuel_type.lower():
            continue

        # Brand / Model filter
        if b_filter:
            name_low = car["name"].lower()
            brand_low = car["brand"].lower()
            if b_filter not in name_low and b_filter not in brand_low:
                continue

        results.append(car)

    return results

# --- ERA: 2018–2025 COMPREHENSIVE INDIAN AUTOMOTIVE REGISTRY ---
RECENT_CAR_CATALOG: List[Dict[str, Any]] = [
    # 2018 Launches
    {
        "name": "Mahindra Marazzo",
        "brand": "Mahindra",
        "launch_year": 2018,
        "category": "MPV",
        "segment": "Premium MPV",
        "fuel_type": "diesel",
        "engine": "1.5L D15 Turbo Diesel (121 HP / 300 Nm)",
        "price_era": "₹9.99 – ₹13.90 Lakh",
        "ex_showroom_price": 1050000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Shark-inspired body-on-frame 7/8 seater MPV with 4-Star Global NCAP safety."
    },
    {
        "name": "Hyundai Santro (2nd Gen)",
        "brand": "Hyundai",
        "launch_year": 2018,
        "category": "Hatchback",
        "segment": "Tall-Boy Family Hatchback",
        "fuel_type": "petrol",
        "engine": "1.1L 4-Cylinder Epsilon (69 HP / 99 Nm)",
        "price_era": "₹3.90 – ₹5.65 Lakh",
        "ex_showroom_price": 425000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Modern comeback of India's favorite tall-boy family hatchback with Smart Auto AMT and rear AC vents."
    },
    {
        "name": "Volvo XC40",
        "brand": "Volvo",
        "launch_year": 2018,
        "category": "luxury",
        "segment": "Compact Luxury SUV",
        "fuel_type": "diesel",
        "engine": "2.0L D4 Twin-Turbo Diesel (190 HP / 400 Nm)",
        "price_era": "₹39.90 – ₹43.90 Lakh",
        "ex_showroom_price": 4150000.0,
        "status": "launched",
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "European Car of the Year winner launched in India with Level 2 ADAS (Pilot Assist) and Thor's Hammer LED headlights."
    },

    # 2019 Launches
    {
        "name": "Kia Seltos (1st Gen)",
        "brand": "Kia",
        "launch_year": 2019,
        "category": "suv",
        "segment": "Midsize SUV",
        "fuel_type": "petrol",
        "engine": "1.4L Turbo GDI (140 HP) / 1.5L CRDi Diesel (115 HP)",
        "price_era": "₹9.69 – ₹15.99 Lakh",
        "ex_showroom_price": 1050000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Kia's blockbuster debut in India in August 2019 featuring UVO connected car tech, Bose 8-speaker audio, and Heads-Up Display."
    },
    {
        "name": "MG Hector",
        "brand": "MG",
        "launch_year": 2019,
        "category": "suv",
        "segment": "Connected Midsize SUV",
        "fuel_type": "petrol",
        "engine": "1.5L Turbo Petrol (143 HP) / 2.0L Multijet Diesel (170 HP)",
        "price_era": "₹12.18 – ₹16.88 Lakh",
        "ex_showroom_price": 1280000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "India's first internet SUV with built-in eSIM, 10.4-inch portrait touchscreen, and panoramic sunroof."
    },
    {
        "name": "Hyundai Kona Electric",
        "brand": "Hyundai",
        "launch_year": 2019,
        "category": "ev",
        "segment": "Electric Compact SUV",
        "fuel_type": "electric",
        "engine": "39.2 kWh Battery (136 HP / 395 Nm | 452 km ARAI Range)",
        "price_era": "₹25.30 – ₹25.50 Lakh",
        "ex_showroom_price": 2530000.0,
        "status": "launched",
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "India's first long-range electric SUV launched in July 2019, pioneering mainstream EV ownership."
    },
    {
        "name": "BMW 3 Series (G20)",
        "brand": "BMW",
        "launch_year": 2019,
        "category": "luxury",
        "segment": "Luxury Sports Sedan",
        "fuel_type": "petrol",
        "engine": "330i 2.0L Turbo Petrol (258 HP / 400 Nm)",
        "price_era": "₹41.40 – ₹47.90 Lakh",
        "ex_showroom_price": 4450000.0,
        "status": "launched",
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "7th-generation 3 Series with BMW Live Cockpit Professional, wireless Apple CarPlay, and 5.8s 0-100 km/h acceleration."
    },

    # 2020 Launches
    {
        "name": "Hyundai Creta (2nd Gen)",
        "brand": "Hyundai",
        "launch_year": 2020,
        "category": "suv",
        "segment": "Midsize SUV",
        "fuel_type": "petrol",
        "engine": "1.4L Turbo GDI / 1.5L Petrol / 1.5L CRDi Diesel (115–140 HP)",
        "price_era": "₹9.99 – ₹17.20 Lakh",
        "ex_showroom_price": 1050000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Trio beam LED headlights, voice-enabled panoramic sunroof, and paddle shifters; dominated Indian SUV sales."
    },
    {
        "name": "Mahindra Thar (2nd Gen 4x4)",
        "brand": "Mahindra",
        "launch_year": 2020,
        "category": "suv",
        "segment": "Lifestyle 4x4 Off-Road SUV",
        "fuel_type": "diesel",
        "engine": "2.2L mHawk Diesel (130 HP) / 2.0L mStallion Turbo Petrol (150 HP)",
        "price_era": "₹9.80 – ₹13.75 Lakh",
        "ex_showroom_price": 1150000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched October 2020 with 4-Star Global NCAP safety, shift-on-fly 4WD transfer case, and removable hard top."
    },
    {
        "name": "Tata Nexon EV (1st Gen)",
        "brand": "Tata Motors",
        "launch_year": 2020,
        "category": "ev",
        "segment": "Electric Compact SUV",
        "fuel_type": "electric",
        "engine": "30.2 kWh Ziptron Battery (129 HP / 245 Nm | 312 km ARAI Range)",
        "price_era": "₹13.99 – ₹15.99 Lakh",
        "ex_showroom_price": 1450000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched January 2020, became India's #1 best-selling electric vehicle with Ziptron high-voltage architecture."
    },
    {
        "name": "Kia Sonet",
        "brand": "Kia",
        "launch_year": 2020,
        "category": "suv",
        "segment": "Sub-4m Compact SUV",
        "fuel_type": "diesel",
        "engine": "1.5L CRDi Diesel (115 HP / 6-Speed Torque Converter AT)",
        "price_era": "₹6.71 – ₹11.99 Lakh",
        "ex_showroom_price": 820000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched September 2020 with segment-first ventilated front seats and 10.25-inch infotainment screen."
    },

    # 2021 Launches
    {
        "name": "Mahindra XUV700",
        "brand": "Mahindra",
        "launch_year": 2021,
        "category": "suv",
        "segment": "Mid-to-Full Size SUV",
        "fuel_type": "diesel",
        "engine": "2.2L mHawk Diesel (185 HP / 450 Nm) / 2.0L Turbo Petrol (200 HP)",
        "price_era": "₹11.99 – ₹22.89 Lakh",
        "ex_showroom_price": 1399000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched August 2021 bringing Level 2 ADAS, Alexa integration, and dual 10.25-inch superscreens under ₹25 lakh."
    },
    {
        "name": "Tata Punch",
        "brand": "Tata Motors",
        "launch_year": 2021,
        "category": "suv",
        "segment": "Micro SUV",
        "fuel_type": "petrol",
        "engine": "1.2L Revotron 3-Cylinder Petrol (86 HP / 115 Nm)",
        "price_era": "₹5.49 – ₹9.09 Lakh",
        "ex_showroom_price": 600000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched October 2021 with 5-Star Global NCAP safety, 187mm ground clearance, and 90-degree wide opening doors."
    },
    {
        "name": "Skoda Kushaq",
        "brand": "Skoda",
        "launch_year": 2021,
        "category": "suv",
        "segment": "European Compact SUV",
        "fuel_type": "petrol",
        "engine": "1.0L TSI (115 HP) / 1.5L TSI EVO Active Cylinder Tech (150 HP)",
        "price_era": "₹10.50 – ₹17.60 Lakh",
        "ex_showroom_price": 1150000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "First localized vehicle under VW Group's India 2.0 MQB-A0-IN platform with 5-Star Global NCAP rating."
    },

    # 2022 Launches
    {
        "name": "Mahindra Scorpio-N",
        "brand": "Mahindra",
        "launch_year": 2022,
        "category": "suv",
        "segment": "D-Segment 4x4 SUV",
        "fuel_type": "diesel",
        "engine": "2.2L mHawk Diesel (175 HP / 400 Nm) / 2.0L Turbo Petrol (203 HP)",
        "price_era": "₹11.99 – ₹23.90 Lakh",
        "ex_showroom_price": 1360000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched June 2022 as 'The Big Daddy of SUVs' with 4XPLOR terrain management and 5-Star Global NCAP safety."
    },
    {
        "name": "Maruti Grand Vitara / Toyota Urban Cruiser Hyryder",
        "brand": "Maruti Suzuki / Toyota",
        "launch_year": 2022,
        "category": "suv",
        "segment": "Strong Hybrid Midsize SUV",
        "fuel_type": "hybrid",
        "engine": "1.5L Intelligent Electric Hybrid e-CVT (27.97 km/l ARAI)",
        "price_era": "₹10.45 – ₹19.65 Lakh",
        "ex_showroom_price": 1120000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Jointly developed self-charging strong hybrid SUV delivering 27.97 km/l mileage with EV-only drive mode and AllGrip AWD."
    },
    {
        "name": "Kia EV6",
        "brand": "Kia",
        "launch_year": 2022,
        "category": "ev",
        "segment": "Luxury Electric Crossover",
        "fuel_type": "electric",
        "engine": "77.4 kWh Battery AWD Dual Motor (325 HP / 605 Nm | 708 km Range)",
        "price_era": "₹59.95 – ₹64.95 Lakh",
        "ex_showroom_price": 6095000.0,
        "status": "launched",
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "800V ultra-fast charging E-GMP architecture capable of 10-80% charge in 18 minutes with V2L power delivery."
    },

    # 2023 Launches
    {
        "name": "Hyundai Exter",
        "brand": "Hyundai",
        "launch_year": 2023,
        "category": "suv",
        "segment": "Micro SUV",
        "fuel_type": "petrol",
        "engine": "1.2L Kappa 4-Cylinder (83 HP) / CNG (69 HP)",
        "price_era": "₹5.99 – ₹10.15 Lakh",
        "ex_showroom_price": 640000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched July 2023 with 6 airbags standard across all variants, dashcam with dual cameras, and voice sunroof."
    },
    {
        "name": "Maruti Jimny 5-Door 4x4",
        "brand": "Maruti Suzuki",
        "launch_year": 2023,
        "category": "suv",
        "segment": "Purist Off-Road 4x4 SUV",
        "fuel_type": "petrol",
        "engine": "1.5L K15B Petrol (105 HP / 134 Nm | AllGrip Pro 4WD)",
        "price_era": "₹12.74 – ₹15.05 Lakh",
        "ex_showroom_price": 1274000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Global debut of 5-door Jimny in India with ladder-frame chassis, 3-link rigid axle suspension, and low-range transfer case."
    },
    {
        "name": "Tata Nexon Facelift (2023)",
        "brand": "Tata Motors",
        "launch_year": 2023,
        "category": "suv",
        "segment": "Compact SUV (Facelift)",
        "fuel_type": "petrol",
        "engine": "1.2L Turbo Petrol (120 HP / 7-Speed DCA) / 1.5L Diesel (115 HP)",
        "price_era": "₹8.10 – ₹15.50 Lakh",
        "ex_showroom_price": 890000.0,
        "status": "facelift",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Curvv-inspired sequential LED DRLs, 2-spoke illuminated steering wheel, and 10.25-inch high-res infotainment."
    },
    {
        "name": "Hyundai Ioniq 5",
        "brand": "Hyundai",
        "launch_year": 2023,
        "category": "ev",
        "segment": "Luxury Electric Crossover",
        "fuel_type": "electric",
        "engine": "72.6 kWh Battery (217 HP / 350 Nm | 631 km ARAI Range)",
        "price_era": "₹44.95 – ₹46.05 Lakh",
        "ex_showroom_price": 4595000.0,
        "status": "launched",
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "World Car of the Year assembled in India with parametric pixel lighting, sliding Universal Island center console, and V2L."
    },

    # 2024 Launches
    {
        "name": "Hyundai Creta Facelift (2024)",
        "brand": "Hyundai",
        "launch_year": 2024,
        "category": "suv",
        "segment": "Midsize SUV (Facelift)",
        "fuel_type": "petrol",
        "engine": "1.5L Turbo GDI (160 HP / 7-Speed DCT) / 1.5L CRDi Diesel (116 HP)",
        "price_era": "₹11.00 – ₹20.15 Lakh",
        "ex_showroom_price": 1100000.0,
        "status": "facelift",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched January 2024 with Horizon LED positioning lamps, Level 2 ADAS with 19 safety features, and 360-degree blind-spot monitor."
    },
    {
        "name": "Mahindra Thar Roxx (5-Door)",
        "brand": "Mahindra",
        "launch_year": 2024,
        "category": "suv",
        "segment": "5-Door Lifestyle Off-Road SUV",
        "fuel_type": "diesel",
        "engine": "2.2L mHawk Diesel (175 HP) / 2.0L mStallion Petrol (177 HP)",
        "price_era": "₹12.99 – ₹22.49 Lakh",
        "ex_showroom_price": 1399000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched August 15, 2024 with extended wheelbase, panoramic Skyroof, Harman Kardon 9-speaker audio, Level 2 ADAS, and 5-Star Bharat NCAP safety."
    },
    {
        "name": "Tata Curvv EV & ICE",
        "brand": "Tata Motors",
        "launch_year": 2024,
        "category": "suv",
        "segment": "Coupe SUV",
        "fuel_type": "electric",
        "engine": "55 kWh Battery (167 HP | 585 km Range) / 1.2L Hyperion Turbo (125 HP)",
        "price_era": "₹17.49 – ₹21.99 Lakh (EV) / ₹9.99 – ₹17.69 Lakh (ICE)",
        "ex_showroom_price": 1749000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "India's first mass-market Coupe SUV launched August 2024 with flush door handles, gesture-controlled power tailgate, and 5-Star Bharat NCAP."
    },
    {
        "name": "Mahindra XUV 3XO",
        "brand": "Mahindra",
        "launch_year": 2024,
        "category": "suv",
        "segment": "Compact SUV (Facelift)",
        "fuel_type": "petrol",
        "engine": "1.2L mStallion TGDi Turbo (130 HP / 230 Nm | 6-Speed AISIN AT)",
        "price_era": "₹7.49 – ₹15.49 Lakh",
        "ex_showroom_price": 850000.0,
        "status": "facelift",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched April 2024 with segment-first panoramic sunroof, Level 2 ADAS, and dual 10.25-inch digital screens."
    },
    {
        "name": "Maruti Suzuki Dzire (4th Gen 2024)",
        "brand": "Maruti Suzuki",
        "launch_year": 2024,
        "category": "Sedan",
        "segment": "Compact Sedan",
        "fuel_type": "petrol",
        "engine": "1.2L 3-Cylinder Z-Series (82 HP / 25.71 km/l ARAI)",
        "price_era": "₹6.79 – ₹10.14 Lakh",
        "ex_showroom_price": 725000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched November 2024; first Maruti vehicle to score 5-Star Global NCAP safety rating, featuring single-pane electric sunroof."
    },
    {
        "name": "MG Windsor EV",
        "brand": "MG",
        "launch_year": 2024,
        "category": "ev",
        "segment": "Electric Crossover Utility Vehicle",
        "fuel_type": "electric",
        "engine": "38 kWh Prismatic Cell Battery (136 HP | 332 km Range)",
        "price_era": "₹9.99 Lakh (+ ₹3.5/km BaaS) or ₹13.50 – ₹15.50 Lakh",
        "ex_showroom_price": 1350000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched September 2024 with 135-degree reclining Aero Lounge rear seats, 15.6-inch Grandview touchscreen, and BaaS battery rental model."
    },

    # 2025 Launches / Upcoming
    {
        "name": "Skoda Kylaq",
        "brand": "Skoda",
        "launch_year": 2025,
        "category": "suv",
        "segment": "Sub-4m Compact SUV",
        "fuel_type": "petrol",
        "engine": "1.0L TSI Turbo Petrol (115 HP / 178 Nm)",
        "price_era": "₹7.89 – ₹14.40 Lakh",
        "ex_showroom_price": 789000.0,
        "status": "launched",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Launched January 2025 as Skoda's entry-level sub-4m compact SUV on MQB-A0-IN platform with 6-way electric seats and 189mm clearance."
    },
    {
        "name": "Tata Sierra EV",
        "brand": "Tata Motors",
        "launch_year": 2025,
        "category": "ev",
        "segment": "Electric Lifestyle SUV",
        "fuel_type": "electric",
        "engine": "60 kWh Gen 2 acti.ev Architecture (500+ km Range)",
        "price_era": "₹22.00 – ₹28.00 Lakh (Est.)",
        "ex_showroom_price": 2400000.0,
        "status": "upcoming",
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "Modern reimagining of India's legendary 1990s lifestyle SUV with curved rear glass lounge and dual-motor AWD."
    },
    {
        "name": "Mahindra BE.05",
        "brand": "Mahindra",
        "launch_year": 2025,
        "category": "ev",
        "segment": "Electric Sports SUV",
        "fuel_type": "electric",
        "engine": "79 kWh INGLO Architecture (285 HP / 550 km Range)",
        "price_era": "₹24.00 – ₹30.00 Lakh (Est.)",
        "ex_showroom_price": 2500000.0,
        "status": "upcoming",
        "is_luxury": True,
        "is_vintage_classic": False,
        "description": "Born Electric SUV built on INGLO skateboard platform with driver-centric fighter-jet cockpit and ultra-fast 175 kW DC charging."
    },
    {
        "name": "Hyundai Creta EV",
        "brand": "Hyundai",
        "launch_year": 2025,
        "category": "ev",
        "segment": "Electric Midsize SUV",
        "fuel_type": "electric",
        "engine": "45 kWh Battery Pack (138 HP | 450 km Estimated Range)",
        "price_era": "₹18.00 – ₹24.00 Lakh (Est.)",
        "ex_showroom_price": 1950000.0,
        "status": "upcoming",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "All-electric version of Hyundai Creta featuring closed-off aero grille, steering-column gear selector, and V2L."
    },
    {
        "name": "Maruti Suzuki e-Vitara",
        "brand": "Maruti Suzuki",
        "launch_year": 2025,
        "category": "ev",
        "segment": "Electric SUV",
        "fuel_type": "electric",
        "engine": "49 kWh & 61 kWh Blade Battery (ALLGRIP-e AWD | 500 km Range)",
        "price_era": "₹20.00 – ₹25.00 Lakh (Est.)",
        "ex_showroom_price": 2100000.0,
        "status": "upcoming",
        "is_luxury": False,
        "is_vintage_classic": False,
        "description": "Maruti's first global EV debut based on Heartect-e platform with BYD LFP blade batteries and electronic 4WD."
    }
]

# Merge recent catalog into master catalog
HISTORICAL_CAR_CATALOG.extend(RECENT_CAR_CATALOG)
