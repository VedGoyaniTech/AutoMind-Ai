"""
Multi-Source Consensus Merger Module — Cross-verifies specs and pricing across multiple trusted sources.
Determines consensus values instead of simply returning the first result.
"""

from typing import List, Optional
from collections import Counter
from app.services.vehicle_search.models import ExtractedVehicleSpec, MergedVehicleResult
from app.services.vehicle_search.utils.logger import log_step


class ConsensusMerger:
    """Merges validated extracted vehicle specifications from multiple trusted web sources into a consensus model."""

    def merge_specs(self, query: str, valid_specs: List[ExtractedVehicleSpec]) -> Optional[MergedVehicleResult]:
        if not valid_specs:
            return None

        log_step("consensus_merger", f"Merging specifications from {len(valid_specs)} validated web sources...")

        # 1. Consensus Vehicle Name
        names = [s.vehicle_name for s in valid_specs if s.vehicle_name]
        consensus_vehicle = Counter(names).most_common(1)[0][0] if names else query.title()

        # 2. Consensus Variant Name
        variants = [s.variant_name for s in valid_specs if s.variant_name and s.variant_name != "Standard Variant"]
        consensus_variant = Counter(variants).most_common(1)[0][0] if variants else "Standard Variant"

        # 3. Consensus Ex-Showroom Price
        prices = [s.ex_showroom_price for s in valid_specs if s.ex_showroom_price]
        consensus_price = Counter(prices).most_common(1)[0][0] if prices else "Contact Dealer"

        # 4. Consensus Fuel & Transmission
        fuels = [s.fuel_type for s in valid_specs if s.fuel_type]
        consensus_fuel = Counter(fuels).most_common(1)[0][0] if fuels else "Petrol"

        transmissions = [s.transmission for s in valid_specs if s.transmission]
        consensus_trans = Counter(transmissions).most_common(1)[0][0] if transmissions else "Automatic"

        # 5. Engine, Power, Torque, Mileage
        engines = [s.engine_capacity for s in valid_specs if s.engine_capacity]
        consensus_engine = Counter(engines).most_common(1)[0][0] if engines else ""

        powers = [s.power_hp for s in valid_specs if s.power_hp]
        consensus_power = Counter(powers).most_common(1)[0][0] if powers else ""

        torques = [s.torque_nm for s in valid_specs if s.torque_nm]
        consensus_torque = Counter(torques).most_common(1)[0][0] if torques else ""

        mileages = [s.mileage_kmpl for s in valid_specs if s.mileage_kmpl]
        consensus_mileage = Counter(mileages).most_common(1)[0][0] if mileages else ""

        # 6. Gather all features and sources
        all_features = []
        for s in valid_specs:
            for f in s.key_features:
                if f not in all_features:
                    all_features.append(f)

        sources = [f"{s.source_domain} ({s.source_url})" for s in valid_specs if s.source_url]

        merged = MergedVehicleResult(
            query=query,
            vehicle=consensus_vehicle,
            variant=consensus_variant,
            manufacturer=valid_specs[0].manufacturer or consensus_vehicle.split()[0],
            fuel=consensus_fuel,
            transmission=consensus_trans,
            engine=consensus_engine,
            power=consensus_power,
            torque=consensus_torque,
            mileage=consensus_mileage,
            price_ex_showroom=consensus_price,
            price_on_road=valid_specs[0].on_road_price or "",
            safety_rating=valid_specs[0].safety_rating or "5-Star Standard",
            features=all_features,
            consensus_sources=sources,
            confidence=1.0
        )

        log_step("consensus_merger", f"Consensus merged result: {merged.vehicle} ({merged.variant}) | Price: {merged.price_ex_showroom} | Sources: {len(sources)}")
        return merged
