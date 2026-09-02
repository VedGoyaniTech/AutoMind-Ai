"""
AutoMind AI — City to State Mapping & Normalization Engine
Maps Indian cities and aliases to standardized state codes (GJ, MH, DL, KA, etc.)
"""

import re
from typing import Optional, Dict, Tuple, List

# Standardized City to State Registry
CITY_STATE_MAP: Dict[str, str] = {
    # ── Gujarat (GJ) ──
    "ahmedabad": "GJ",
    "amdavad": "GJ",
    "ahmadabad": "GJ",
    "surat": "GJ",
    "vadodara": "GJ",
    "baroda": "GJ",
    "rajkot": "GJ",
    "gandhinagar": "GJ",
    "bhavnagar": "GJ",
    "jamnagar": "GJ",
    "junagadh": "GJ",
    "anand": "GJ",
    "navsari": "GJ",
    "morbi": "GJ",
    "vapi": "GJ",
    "bharuch": "GJ",

    # ── Maharashtra (MH) ──
    "mumbai": "MH",
    "bombay": "MH",
    "pune": "MH",
    "nagpur": "MH",
    "thane": "MH",
    "nashik": "MH",
    "nasik": "MH",
    "aurangabad": "MH",
    "chhatrapati sambhajinagar": "MH",
    "solapur": "MH",
    "navi mumbai": "MH",
    "kolhapur": "MH",
    "amravati": "MH",
    "jalgaon": "MH",
    "akola": "MH",

    # ── Delhi NCR (DL) ──
    "delhi": "DL",
    "new delhi": "DL",
    "dilli": "DL",
    "ncr": "DL",
    "delhi ncr": "DL",
    "noida": "DL",       # Standardized fallback for NCR queries
    "gurgaon": "DL",
    "gurugram": "DL",
    "faridabad": "DL",
    "ghaziabad": "DL",

    # ── Karnataka (KA) ──
    "bengaluru": "KA",
    "bangalore": "KA",
    "blr": "KA",
    "mysuru": "KA",
    "mysore": "KA",
    "hubballi": "KA",
    "hubli": "KA",
    "mangaluru": "KA",
    "mangalore": "KA",
    "belagavi": "KA",
    "belgaum": "KA",
    "kalaburagi": "KA",
    "gulbarga": "KA",
    "davangere": "KA",
    "ballari": "KA",
    "bellary": "KA"
}

STATE_NAMES: Dict[str, str] = {
    "GJ": "Gujarat",
    "MH": "Maharashtra",
    "DL": "Delhi",
    "KA": "Karnataka",
    "TN": "Tamil Nadu",
    "KL": "Kerala",
    "RJ": "Rajasthan",
    "UP": "Uttar Pradesh",
    "TS": "Telangana",
    "AP": "Andhra Pradesh",
    "WB": "West Bengal",
    "PB": "Punjab",
    "HR": "Haryana"
}

def normalize_city_and_state(
    city: Optional[str] = None,
    state_code: Optional[str] = None
) -> Tuple[str, str, str]:
    """
    Normalizes city and state inputs.
    Returns: (canonical_city_name, canonical_state_code, scope_description)
    """
    # 1. If city is provided, look up state
    if city and city.strip():
        clean_city = re.sub(r'[^a-zA-Z\s]', '', city.strip().lower()).strip()
        if clean_city in CITY_STATE_MAP:
            mapped_state = CITY_STATE_MAP[clean_city]
            canonical_city = clean_city.title()
            return canonical_city, mapped_state, f"City-specific estimate for {canonical_city}, {STATE_NAMES.get(mapped_state, mapped_state)}"

    # 2. If state code is provided and valid
    if state_code and state_code.strip():
        clean_state = state_code.strip().upper()
        if clean_state in STATE_NAMES:
            fallback_city = {
                "GJ": "Ahmedabad",
                "MH": "Mumbai",
                "DL": "Delhi",
                "KA": "Bengaluru"
            }.get(clean_state, "State Baseline")
            return fallback_city, clean_state, f"State-level baseline estimate for {STATE_NAMES.get(clean_state, clean_state)}"

    # 3. If neither or invalid, raise clear validation error
    supported_cities = ["Ahmedabad", "Surat", "Mumbai", "Pune", "Delhi", "Bengaluru", "Mysuru"]
    raise ValueError(
        f"Could not resolve city/state from city='{city}' or stateCode='{state_code}'. "
        f"Supported states: ['GJ', 'MH', 'DL', 'KA']. Supported major cities include: {supported_cities}"
    )

def extract_city_or_state_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Scans a conversational prompt in English, Hindi, or Gujarati for known cities or state codes.
    Prioritizes specific city names before falling back to state-level identifiers.
    """
    text_lower = text.lower()

    # 1. Check specific city names and aliases FIRST
    # Sort cities by length descending to match longest substring e.g. "new delhi" before "delhi"
    sorted_cities = sorted(CITY_STATE_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    for city, state in sorted_cities:
        # Use word boundary where possible
        pattern = r'(?:\b|^)' + re.escape(city) + r'(?:\b|$)'
        if re.search(pattern, text_lower):
            return city.title(), state

    # 2. Check full state names
    for code, name in [("GJ", "gujarat"), ("MH", "maharashtra"), ("DL", "delhi"), ("KA", "karnataka")]:
        if name in text_lower:
            return None, code

    # 3. Check explicit state codes (avoiding false positive for Hindi preposition "ka")
    for code in ["GJ", "MH", "DL"]:
        if re.search(r'\b' + re.escape(code.lower()) + r'\b', text_lower):
            return None, code

    # For KA, match only if uppercase "KA" in original text or explicit "state ka" / "rto ka"
    if re.search(r'\bKA\b', text) or re.search(r'\b(?:state|rto|code)\s+ka\b', text_lower):
        return None, "KA"

    return None, None
