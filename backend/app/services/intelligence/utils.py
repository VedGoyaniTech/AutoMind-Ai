import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

def calculate_market_statistics(
    listings: List[Dict[str, Any]],
    currency: str = "USD"
) -> Dict[str, Any]:
    """
    Computes genuine market statistics from a collection of active listings:
    - Number of matching listings
    - Minimum, maximum, average, and median asking prices
    - Price distribution buckets
    - Mileage distribution (average, min, max)
    - Average listing age in days (when listing dates are present)
    - Clear distinction that values represent asking prices, not completed transactions.
    """
    if not listings:
        return {
            "total_listings": 0,
            "currency": currency,
            "has_sufficient_data": False,
            "min_asking_price": None,
            "max_asking_price": None,
            "average_asking_price": None,
            "median_asking_price": None,
            "price_distribution": [],
            "mileage_statistics": None,
            "listing_age_statistics": None,
            "trend_indicator": "insufficient_data",
            "market_disclaimer": "All figures represent current seller/dealer asking prices, not verified final transaction amounts. Insufficient historical points for trend projection."
        }

    prices = []
    mileages = []
    ages_days = []
    now = datetime.now(timezone.utc)

    for item in listings:
        p = item.get("price")
        if p is not None and isinstance(p, (int, float)) and p > 0:
            prices.append(float(p))

        m = item.get("mileage")
        if m is not None and isinstance(m, (int, float)) and m >= 0:
            mileages.append(float(m))

        listed_at = item.get("listed_at")
        if listed_at:
            if isinstance(listed_at, str):
                try:
                    dt = datetime.fromisoformat(listed_at.replace("Z", "+00:00"))
                    ages_days.append(max(0, (now - dt).days))
                except Exception:
                    pass
            elif isinstance(listed_at, datetime):
                ages_days.append(max(0, (now - listed_at).days))

    if not prices:
        return {
            "total_listings": len(listings),
            "currency": currency,
            "has_sufficient_data": False,
            "min_asking_price": None,
            "max_asking_price": None,
            "average_asking_price": None,
            "median_asking_price": None,
            "price_distribution": [],
            "mileage_statistics": None,
            "listing_age_statistics": None,
            "trend_indicator": "insufficient_data",
            "market_disclaimer": "Listing records present without valid numeric asking prices."
        }

    prices.sort()
    count = len(prices)
    min_p = prices[0]
    max_p = prices[-1]
    avg_p = round(sum(prices) / count, 2)

    # Median
    if count % 2 == 1:
        median_p = prices[count // 2]
    else:
        median_p = round((prices[count // 2 - 1] + prices[count // 2]) / 2.0, 2)

    # Price distribution buckets (up to 4 equal width buckets)
    distribution = []
    if min_p == max_p or count <= 2:
        distribution.append({
            "range_label": f"{currency} {min_p:,.0f}",
            "min": min_p,
            "max": max_p,
            "count": count,
            "percentage": 100.0
        })
    else:
        bucket_count = min(4, count)
        step = (max_p - min_p) / bucket_count
        for i in range(bucket_count):
            b_min = round(min_p + i * step, 2)
            b_max = round(min_p + (i + 1) * step, 2)
            b_items = [p for p in prices if (b_min <= p <= b_max if i == bucket_count - 1 else b_min <= p < b_max)]
            distribution.append({
                "range_label": f"{currency} {b_min:,.0f} – {b_max:,.0f}",
                "min": b_min,
                "max": b_max,
                "count": len(b_items),
                "percentage": round((len(b_items) / count) * 100, 1)
            })

    # Mileage stats
    mileage_stats = None
    if mileages:
        mileages.sort()
        mileage_stats = {
            "count": len(mileages),
            "unit": listings[0].get("mileage_unit", "miles"),
            "average": round(sum(mileages) / len(mileages), 1),
            "min": mileages[0],
            "max": mileages[-1]
        }

    # Listing age stats
    age_stats = None
    if ages_days:
        age_stats = {
            "count": len(ages_days),
            "average_days_on_market": round(sum(ages_days) / len(ages_days), 1),
            "min_days": min(ages_days),
            "max_days": max(ages_days)
        }

    return {
        "total_listings": count,
        "currency": currency,
        "has_sufficient_data": count >= 3,
        "min_asking_price": min_p,
        "max_asking_price": max_p,
        "average_asking_price": avg_p,
        "median_asking_price": median_p,
        "price_distribution": distribution,
        "mileage_statistics": mileage_stats,
        "listing_age_statistics": age_stats,
        "trend_indicator": "stable_sample" if count >= 5 else "preliminary_sample",
        "market_disclaimer": "Figures reflect active dealer/seller asking prices. Actual transaction values may differ depending on negotiation, vehicle condition, and documentation fees."
    }


def normalize_vehicle_specs(raw: Dict[str, Any], provider: str) -> Dict[str, Any]:
    """
    Normalizes specifications returned from external providers (Vehicles.dev, NHTSA vPIC, etc.)
    into a standardized schema for AutoMind AI.
    """
    if provider == "nhtsa":
        return {
            "provider": "NHTSA vPIC",
            "make": raw.get("Make") or raw.get("make"),
            "model": raw.get("Model") or raw.get("model"),
            "model_year": raw.get("ModelYear") or raw.get("model_year"),
            "body_class": raw.get("BodyClass") or raw.get("body_type"),
            "vehicle_type": raw.get("VehicleType"),
            "drive_type": raw.get("DriveType"),
            "engine_cylinders": raw.get("EngineCylinders"),
            "displacement_l": raw.get("DisplacementL"),
            "fuel_type_primary": raw.get("FuelTypePrimary"),
            "plant_country": raw.get("PlantCountry"),
            "gvwr": raw.get("GVWR"),
            "vin": raw.get("VIN"),
            "provenance": "US National Highway Traffic Safety Administration (vPIC API)"
        }
    elif provider == "vehicles_dev":
        return {
            "provider": "Vehicles.dev",
            "make": raw.get("make"),
            "model": raw.get("model"),
            "model_year": raw.get("year"),
            "trim": raw.get("trim") or raw.get("variant"),
            "body_type": raw.get("body_type") or raw.get("body_style"),
            "transmission": raw.get("transmission"),
            "drivetrain": raw.get("drivetrain") or raw.get("drive_type"),
            "engine": raw.get("engine"),
            "horsepower": raw.get("horsepower") or raw.get("hp"),
            "torque": raw.get("torque"),
            "fuel_type": raw.get("fuel_type"),
            "mpg_city": raw.get("mpg_city"),
            "mpg_highway": raw.get("mpg_highway"),
            "vin": raw.get("vin"),
            "provenance": "Vehicles.dev API"
        }
    else:
        return {
            "provider": provider,
            "make": raw.get("make"),
            "model": raw.get("model"),
            "model_year": raw.get("year"),
            "provenance": provider
        }
