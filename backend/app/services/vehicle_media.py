"""
AutoMind AI — Structured Vehicle Media & Image Gallery Service
Provides curated high-resolution automotive imagery categorized by Exterior and Interior.
"""

from typing import Dict, Any, List, Optional
import re

VEHICLE_IMAGE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "thar": {
        "manufacturer": "Mahindra",
        "model": "Thar",
        "tagline": "Iconic 4x4 Off-Road SUV",
        "images": [
            {
                "id": "thar-ext-front",
                "url": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1000&auto=format&fit=crop&q=80",
                "alt": "Mahindra Thar Front Three-Quarter Off-Road",
                "category": "exterior",
                "caption": "Muscular Front Grille & All-Terrain Stance"
            },
            {
                "id": "thar-ext-side",
                "url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1000&auto=format&fit=crop&q=80",
                "alt": "Mahindra Thar High Ground Clearance Profile",
                "category": "exterior",
                "caption": "226mm Ground Clearance & 18-inch Alloys"
            }
        ]
    },
    "creta": {
        "manufacturer": "Hyundai",
        "model": "Creta",
        "tagline": "India's Best-Selling Midsize SUV",
        "images": [
            {
                "id": "creta-ext-front",
                "url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=1000&auto=format&fit=crop&q=80",
                "alt": "Hyundai Creta Connected Horizon LED DRLs",
                "category": "exterior",
                "caption": "Parametric Black Chrome Grille & Horizon LED DRLs"
            },
            {
                "id": "creta-int-cabin",
                "url": "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=1000&auto=format&fit=crop&q=80",
                "alt": "Hyundai Creta Panoramic Cockpit",
                "category": "interior",
                "caption": "Dual 10.25-inch Screens & Ventilated Seats"
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
                "url": "https://images.unsplash.com/photo-1502877338535-766e1452684a?w=1000&auto=format&fit=crop&q=80",
                "alt": "Tata Nexon Bi-LED Headlights & Stance",
                "category": "exterior",
                "caption": "Sequential Dynamic LED DRLs & Aerodynamic Stance"
            },
            {
                "id": "nexon-int-cabin",
                "url": "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1000&auto=format&fit=crop&q=80",
                "alt": "Tata Nexon Digital Cockpit & Steering",
                "category": "interior",
                "caption": "10.25-inch Digital Cockpit & Touch Climate Panel"
            }
        ]
    },
    "curvv": {
        "manufacturer": "Tata",
        "model": "Curvv",
        "tagline": "Futuristic Aerodynamic Coupe SUV",
        "images": [
            {
                "id": "curvv-ext-front",
                "url": "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=1000&auto=format&fit=crop&q=80",
                "alt": "Tata Curvv Aerodynamic Coupe Roofline",
                "category": "exterior",
                "caption": "Sloping Fastback Silhouette & Flush Door Handles"
            }
        ]
    },
    "xuv700": {
        "manufacturer": "Mahindra",
        "model": "XUV700",
        "tagline": "Flagship 7-Seater Turbo SUV",
        "images": [
            {
                "id": "xuv700-ext-front",
                "url": "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=1000&auto=format&fit=crop&q=80",
                "alt": "Mahindra XUV700 Smart Flush Door Handles",
                "category": "exterior",
                "caption": "Arrowhead LED Headlamps & High-Speed Highway Stance"
            }
        ]
    },
    "dzire": {
        "manufacturer": "Maruti Suzuki",
        "model": "Dzire",
        "tagline": "5-Star NCAP High-Efficiency Sedan",
        "images": [
            {
                "id": "dzire-ext-front",
                "url": "https://images.unsplash.com/photo-1590362891991-f776e747a588?w=1000&auto=format&fit=crop&q=80",
                "alt": "Maruti Dzire Sleek Aerodynamic Sedan",
                "category": "exterior",
                "caption": "Crystal LED Headlights & European Sedan Profile"
            }
        ]
    }
}

def get_vehicle_gallery_for_query(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Scans a user query or vehicle model for matching media assets.
    """
    p_lower = prompt.lower()
    # If it's a comparison query, do not return single vehicle gallery
    if any(w in p_lower for w in [" vs ", " versus ", "compare ", "comparison ", "તુલના", "સરખામણી"]):
        return None

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
    return None

get_vehicle_media_gallery = get_vehicle_gallery_for_query
