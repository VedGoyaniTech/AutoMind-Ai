import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Master Normalized Automotive Dataset Repository
VERIFIED_AUTOMOTIVE_DATASET: List[Dict[str, Any]] = [
    # --- 2005 LAUNCHES (INDIA) ---
    {
        "car_name": "Swift (1st Gen)",
        "brand": "Maruti Suzuki",
        "launch_year": 2005,
        "launch_date": "May 2005",
        "status": "launched",
        "country": "India",
        "segment": "Hatchback",
        "category": "mass-market",
        "fuel_type": "Petrol",
        "price": "₹3.87 – ₹4.85 Lakh",
        "source_name": "Maruti Suzuki Official Index",
        "source_url": "https://www.marutisuzuki.com"
    },
    {
        "car_name": "Innova (1st Gen)",
        "brand": "Toyota",
        "launch_year": 2005,
        "launch_date": "February 2005",
        "status": "launched",
        "country": "India",
        "segment": "MUV",
        "category": "mass-market",
        "fuel_type": "Diesel",
        "price": "₹6.75 – ₹10.00 Lakh",
        "source_name": "Toyota Bharat Archives",
        "source_url": "https://www.toyotabharat.com"
    },
    {
        "car_name": "City ZX (3rd Gen)",
        "brand": "Honda",
        "launch_year": 2005,
        "launch_date": "November 2005",
        "status": "launched",
        "country": "India",
        "segment": "Sedan",
        "category": "mass-market",
        "fuel_type": "Petrol",
        "price": "₹6.80 – ₹7.90 Lakh",
        "source_name": "Honda Car India Index",
        "source_url": "https://www.hondacarindia.com"
    },
    {
        "car_name": "Tucson (1st Gen)",
        "brand": "Hyundai",
        "launch_year": 2005,
        "launch_date": "April 2005",
        "status": "launched",
        "country": "India",
        "segment": "SUV",
        "category": "premium",
        "fuel_type": "Diesel",
        "price": "₹14.30 Lakh",
        "source_name": "Hyundai Motor India",
        "source_url": "https://www.hyundai.com/in"
    },
    {
        "car_name": "A6 (C6)",
        "brand": "Audi",
        "launch_year": 2005,
        "launch_date": "March 2005",
        "status": "launched",
        "country": "India",
        "segment": "Sedan",
        "category": "luxury",
        "fuel_type": "Petrol",
        "price": "₹38.00 – ₹45.00 Lakh",
        "source_name": "Audi India Official Portal",
        "source_url": "https://www.audi.in"
    },

    # --- 2024 LAUNCHES (INDIA) ---
    {
        "car_name": "Punch EV",
        "brand": "Tata Motors",
        "launch_year": 2024,
        "launch_date": "January 2024",
        "status": "launched",
        "country": "India",
        "segment": "EV",
        "category": "mass-market",
        "fuel_type": "EV",
        "price": "₹10.99 – ₹15.49 Lakh",
        "source_name": "Tata Motors EV Index",
        "source_url": "https://ev.tatamotors.com"
    },
    {
        "car_name": "Curvv & Curvv EV",
        "brand": "Tata Motors",
        "launch_year": 2024,
        "launch_date": "August 2024",
        "status": "launched",
        "country": "India",
        "segment": "Coupe SUV",
        "category": "mass-market",
        "fuel_type": "EV",
        "price": "₹10.00 – ₹22.00 Lakh",
        "source_name": "CarWale Verified Research",
        "source_url": "https://www.carwale.com"
    },
    {
        "car_name": "Thar Roxx (5-Door)",
        "brand": "Mahindra",
        "launch_year": 2024,
        "launch_date": "August 2024",
        "status": "launched",
        "country": "India",
        "segment": "SUV",
        "category": "mass-market",
        "fuel_type": "Diesel",
        "price": "₹12.99 – ₹20.49 Lakh",
        "source_name": "Mahindra Auto Official",
        "source_url": "https://auto.mahindra.com"
    },
    {
        "car_name": "XUV3XO",
        "brand": "Mahindra",
        "launch_year": 2024,
        "launch_date": "April 2024",
        "status": "launched",
        "country": "India",
        "segment": "SUV",
        "category": "mass-market",
        "fuel_type": "Petrol",
        "price": "₹7.49 – ₹15.49 Lakh",
        "source_name": "Mahindra Auto Official",
        "source_url": "https://auto.mahindra.com"
    },
    {
        "car_name": "Swift (4th Gen)",
        "brand": "Maruti Suzuki",
        "launch_year": 2024,
        "launch_date": "May 2024",
        "status": "launched",
        "country": "India",
        "segment": "Hatchback",
        "category": "mass-market",
        "fuel_type": "Petrol",
        "price": "₹6.49 – ₹9.64 Lakh",
        "source_name": "Maruti Suzuki Arena",
        "source_url": "https://www.marutisuzuki.com"
    },
    {
        "car_name": "Creta Facelift",
        "brand": "Hyundai",
        "launch_year": 2024,
        "launch_date": "January 2024",
        "status": "launched",
        "country": "India",
        "segment": "SUV",
        "category": "mass-market",
        "fuel_type": "Petrol",
        "price": "₹11.00 – ₹20.15 Lakh",
        "source_name": "Hyundai Motor India",
        "source_url": "https://www.hyundai.com/in"
    },
    {
        "car_name": "BYD Seal EV",
        "brand": "BYD",
        "launch_year": 2024,
        "launch_date": "March 2024",
        "status": "launched",
        "country": "India",
        "segment": "Sedan",
        "category": "premium",
        "fuel_type": "EV",
        "price": "₹41.00 – ₹53.00 Lakh",
        "source_name": "BYD Auto India",
        "source_url": "https://www.bydauto.in"
    },
    {
        "car_name": "XUV400 EV (EL Pro)",
        "brand": "Mahindra",
        "launch_year": 2024,
        "launch_date": "January 2024",
        "status": "launched",
        "country": "India",
        "segment": "EV",
        "category": "mass-market",
        "fuel_type": "EV",
        "price": "₹17.49 Lakh",
        "source_name": "EV India Portal",
        "source_url": "https://www.evindia.online"
    },

    # --- 2026 LAUNCHES (INDIA) ---
    {
        "car_name": "EQE SUV & Maybach EQS",
        "brand": "Mercedes-Benz",
        "launch_year": 2026,
        "launch_date": "Q1 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "SUV",
        "category": "luxury",
        "fuel_type": "EV",
        "price": "₹1.40 – ₹2.25 Crore",
        "source_name": "Mercedes-Benz India Official",
        "source_url": "https://www.mercedes-benz.co.in"
    },
    {
        "car_name": "iX1 xDrive30 & i4 Gran Coupe",
        "brand": "BMW",
        "launch_year": 2026,
        "launch_date": "Q1 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "SUV",
        "category": "luxury",
        "fuel_type": "EV",
        "price": "₹66.90 – ₹72.50 Lakh",
        "source_name": "BMW India Portal",
        "source_url": "https://www.bmw.in"
    },
    {
        "car_name": "Q6 e-tron",
        "brand": "Audi",
        "launch_year": 2026,
        "launch_date": "Q2 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "SUV",
        "category": "luxury",
        "fuel_type": "EV",
        "price": "₹85.00 – ₹1.10 Crore",
        "source_name": "Audi India Official Portal",
        "source_url": "https://www.audi.in"
    },
    {
        "car_name": "Macan EV",
        "brand": "Porsche",
        "launch_year": 2026,
        "launch_date": "Q1 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "SUV",
        "category": "supercar",
        "fuel_type": "EV",
        "price": "₹1.65 – ₹2.10 Crore",
        "source_name": "Porsche India Center",
        "source_url": "https://www.porsche.com/india"
    },
    {
        "car_name": "LM 350h",
        "brand": "Lexus",
        "launch_year": 2026,
        "launch_date": "Q1 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "MUV",
        "category": "luxury",
        "fuel_type": "Hybrid",
        "price": "₹2.00 – ₹2.50 Crore",
        "source_name": "Lexus India Portal",
        "source_url": "https://www.lexusindia.co.in"
    },
    {
        "car_name": "Spectre EV",
        "brand": "Rolls-Royce",
        "launch_year": 2026,
        "launch_date": "Q2 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "Coupe",
        "category": "luxury",
        "fuel_type": "EV",
        "price": "₹7.50 Crore+",
        "source_name": "Rolls-Royce Motor Cars",
        "source_url": "https://www.rolls-roycemotorcars.com"
    },
    {
        "car_name": "Sierra EV & Sierra ICE",
        "brand": "Tata Motors",
        "launch_year": 2026,
        "launch_date": "Q1 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "SUV",
        "category": "mass-market",
        "fuel_type": "EV",
        "price": "₹18.00 – ₹25.00 Lakh",
        "source_name": "Tata Motors Official",
        "source_url": "https://www.tatamotors.com"
    },
    {
        "car_name": "eVX / eVitara",
        "brand": "Maruti Suzuki",
        "launch_year": 2026,
        "launch_date": "Q1 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "EV",
        "category": "mass-market",
        "fuel_type": "EV",
        "price": "₹15.00 – ₹22.00 Lakh",
        "source_name": "Maruti Suzuki Arena",
        "source_url": "https://www.marutisuzuki.com"
    },
    {
        "car_name": "Creta EV",
        "brand": "Hyundai",
        "launch_year": 2026,
        "launch_date": "Q1 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "EV",
        "category": "mass-market",
        "fuel_type": "EV",
        "price": "₹17.00 – ₹22.00 Lakh",
        "source_name": "Hyundai Motor India",
        "source_url": "https://www.hyundai.com/in"
    },
    {
        "car_name": "BE.05 Electric SUV",
        "brand": "Mahindra",
        "launch_year": 2026,
        "launch_date": "Q1 2026",
        "status": "upcoming",
        "country": "India",
        "segment": "EV",
        "category": "mass-market",
        "fuel_type": "EV",
        "price": "₹19.00 – ₹24.00 Lakh",
        "source_name": "Mahindra Electric",
        "source_url": "https://auto.mahindra.com"
    }
]

class CarDatasetStore:
    """Centralized verified dataset repository for strict querying across launch years, categories, and markets."""

    @staticmethod
    def query(
        launch_year: Optional[int] = None,
        category: Optional[str] = None,
        fuel_type: Optional[str] = None,
        status: Optional[str] = None,
        market: str = "India"
    ) -> List[Dict[str, Any]]:
        """Strictly query the verified dataset by intent constraints."""
        results = []
        for item in VERIFIED_AUTOMOTIVE_DATASET:
            # 1. Market check
            if market and item.get("country", "").lower() != market.lower():
                continue

            # 2. Strict Launch Year check
            if launch_year is not None and item.get("launch_year") != launch_year:
                continue

            # 3. Category check (luxury, supercar, premium, mass-market)
            if category:
                cat_lower = category.lower()
                item_cat = item.get("category", "").lower()
                if cat_lower in ["luxury", "supercar", "premium"]:
                    if item_cat not in ["luxury", "supercar", "premium"]:
                        continue
                elif cat_lower == "mass-market":
                    if item_cat != "mass-market":
                        continue

            # 4. Fuel type check (EV, Petrol, Diesel, Hybrid, CNG)
            if fuel_type:
                f_lower = fuel_type.lower()
                item_f = item.get("fuel_type", "").lower()
                if f_lower in ["ev", "electric"]:
                    if item_f not in ["ev", "electric"]:
                        continue
                elif f_lower not in item_f:
                    continue

            # 5. Status check (launched vs upcoming)
            if status and status != "any":
                if item.get("status", "").lower() != status.lower():
                    continue

            results.append(item)

        logger.info(
            f"[CarDatasetStore] query filters -> launch_year={launch_year}, category={category}, fuel_type={fuel_type}, status={status}, market={market} | matched={len(results)}"
        )
        return results
