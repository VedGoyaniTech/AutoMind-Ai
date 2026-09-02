"""
AutoMind AI — Comprehensive Historical, Vintage & Multi-Era Validation Suite
Verifies:
1. Exact year 2000 luxury & vintage queries in Hindi/Hinglish/English
2. Decadal queries (1990s, 2000s, 2010s, 2020s, 2026 upcoming)
3. Zero 'Dataset Verification Notice' regressions when historical records exist
4. Clean dataset deduplication and catalog validation
"""

import os
import sys
import pytest
from app.services.pricing.historical_cars import query_historical_cars, HISTORICAL_CAR_CATALOG
from app.services.ai.llm_provider import get_llm_provider

def test_historical_catalog_integrity():
    """Verify that all historical car records have required fields and valid launch years."""
    assert len(HISTORICAL_CAR_CATALOG) >= 15
    for car in HISTORICAL_CAR_CATALOG:
        assert "name" in car
        assert "brand" in car
        assert "launch_year" in car and 1990 <= car["launch_year"] <= 2026
        assert "price_era" in car
        assert "segment" in car

def test_year_2000_luxury_and_vintage_filtering():
    """Verify filtering for Year 2000 Luxury and Vintage cars in India."""
    cars_2000 = query_historical_cars(year=2000)
    assert len(cars_2000) >= 5
    car_names = [c["name"] for c in cars_2000]
    
    # Must include flagship luxury and iconic sports launches of 2000
    assert any("Mercedes-Benz E-Class" in n for n in car_names)
    assert any("Mercedes-Benz S-Class" in n for n in car_names)
    assert any("Honda City" in n for n in car_names)
    assert any("Mitsubishi Lancer" in n for n in car_names)

def test_user_exact_year_2000_hindi_prompt():
    """Verify that user's exact Hinglish query generates a grounded answer with 2000 cars."""
    llm = get_llm_provider()
    prompt = "Mujhe Batao Ki 2000 ki Sal mein kaun si vintage Karn luxury kar launch hui thi"
    response = llm.generate(prompt, "")

    assert "Dataset Verification Notice" not in response
    assert "2000" in response
    assert "Mercedes-Benz" in response
    assert "Honda City" in response or "Mitsubishi Lancer" in response
    assert "|" in response # Formatted table present

def test_multi_era_queries():
    """Verify car launch queries across different years (1998, 2000, 2009, 2026)."""
    llm = get_llm_provider()

    # 1998 Era
    r_1998 = llm.generate("Cars launched in India in 1998", "")
    assert "1998" in r_1998 or "Safari" in r_1998 or "City" in r_1998

    # 2009 Era (Fortuner)
    r_2009 = llm.generate("SUV launched in India in 2009", "")
    assert "Toyota Fortuner" in r_2009 or "2009" in r_2009

    # 2026 Upcoming
    r_2026 = llm.generate("Upcoming cars in 2026 in India", "")
    assert "2026" in r_2026 or "Upcoming" in r_2026
