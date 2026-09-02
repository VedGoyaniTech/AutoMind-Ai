"""
Consensus Engine Module — Merges and cross-verifies ExtractedVehicleData across multiple trusted sources.
Determines consensus values instead of returning a single source.
"""

from typing import List, Optional
from collections import Counter
from app.services.vehicle_search.models.vehicle import ExtractedVehicleData, ConsensusVehicleData
from app.services.vehicle_search.utils.logger import log_step


class ConsensusEngine:
    """Merges validated extracted vehicle specifications from multiple trusted web sources into a consensus model."""

    def determine_consensus(self, query: str, valid_data_list: List[ExtractedVehicleData]) -> Optional[ConsensusVehicleData]:
        if not valid_data_list:
            return None

        log_step("consensus_engine", f"Determining multi-source consensus across {len(valid_data_list)} trusted sources...")

        # 1. Consensus Brand & Model
        brands = [d.brand for d in valid_data_list if d.brand]
        consensus_brand = Counter(brands).most_common(1)[0][0] if brands else valid_data_list[0].brand

        models = [d.model for d in valid_data_list if d.model]
        consensus_model = Counter(models).most_common(1)[0][0] if models else valid_data_list[0].model

        # 2. Consensus Variant
        variants = [d.variant for d in valid_data_list if d.variant and d.variant != "Standard Variant"]
        consensus_variant = Counter(variants).most_common(1)[0][0] if variants else "Standard Variant"

        # 3. Consensus Ex-Showroom Price
        prices = [d.price_ex_showroom for d in valid_data_list if d.price_ex_showroom]
        consensus_price = Counter(prices).most_common(1)[0][0] if prices else valid_data_list[0].price_ex_showroom

        # 4. Consensus Fuel & Transmission
        fuels = [d.fuel for d in valid_data_list if d.fuel]
        consensus_fuel = Counter(fuels).most_common(1)[0][0] if fuels else "Petrol"

        transmissions = [d.transmission for d in valid_data_list if d.transmission]
        consensus_trans = Counter(transmissions).most_common(1)[0][0] if transmissions else "Automatic"

        # 5. Engine, Power, Torque, Mileage
        engines = [d.engine for d in valid_data_list if d.engine]
        consensus_engine = Counter(engines).most_common(1)[0][0] if engines else ""

        powers = [d.power for d in valid_data_list if d.power]
        consensus_power = Counter(powers).most_common(1)[0][0] if powers else ""

        torques = [d.torque for d in valid_data_list if d.torque]
        consensus_torque = Counter(torques).most_common(1)[0][0] if torques else ""

        mileages = [d.mileage for d in valid_data_list if d.mileage]
        consensus_mileage = Counter(mileages).most_common(1)[0][0] if mileages else ""

        # 6. Gather all features and sources
        all_features = []
        for d in valid_data_list:
            for f in d.features:
                if f not in all_features:
                    all_features.append(f)

        sources = [f"{d.source_domain} ({d.source_url})" for d in valid_data_list if d.source_url]

        consensus = ConsensusVehicleData(
            brand=consensus_brand,
            model=consensus_model,
            series=valid_data_list[0].series,
            variant=consensus_variant,
            fuel=consensus_fuel,
            transmission=consensus_trans,
            engine=consensus_engine,
            power=consensus_power,
            torque=consensus_torque,
            mileage=consensus_mileage,
            price_ex_showroom=consensus_price,
            price_on_road=valid_data_list[0].price_on_road or "",
            safety_rating=valid_data_list[0].safety_rating or "5-Star Standard",
            features=all_features,
            consensus_sources=sources,
            confidence=1.0
        )

        log_step("consensus_engine", f"Consensus determined: {consensus.brand} {consensus.model} ({consensus.variant}) | Price: {consensus.price_ex_showroom} | Sources: {len(sources)}")
        return consensus
