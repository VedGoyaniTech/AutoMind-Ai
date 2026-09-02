"""
LLM Formatter Module — Strict JSON-to-Markdown formatter.
Rules:
- Never guess prices
- Never guess variants
- Never guess specifications
- Never merge different vehicles
- Never invent data
- Only format provided validated JSON schema
"""

from typing import Dict, Any, Optional
from app.services.vehicle_search.models.vehicle import ConsensusVehicleData
from app.services.vehicle_search.utils.logger import log_step


class LLMFormatter:
    """Formats validated ConsensusVehicleData JSON payload into clean Markdown reports."""

    def format_consensus_json(self, consensus: ConsensusVehicleData, web_references: Optional[list] = None) -> str:
        if not consensus:
            return "No validated vehicle information could be found."

        log_step("llm_formatter", f"Formatting validated consensus JSON for: {consensus.brand} {consensus.model}")

        brand = consensus.brand
        model = consensus.model
        variant = consensus.variant
        price = consensus.price_ex_showroom or "Contact Dealer"
        onroad = consensus.price_on_road
        fuel = consensus.fuel
        trans = consensus.transmission
        engine = consensus.engine
        power = consensus.power
        torque = consensus.torque
        mileage = consensus.mileage
        safety = consensus.safety_rating
        features = consensus.features

        out = []
        out.append(f"## 🚗 {brand} {model} ({variant}) — Verified Technical Specifications & Pricing\n")
        out.append("### 💰 Validated Pricing & Overview\n")
        out.append("| Property | Spec / Details |")
        out.append("| :--- | :--- |")
        out.append(f"| **Brand & Model** | **{brand} {model}** |")
        out.append(f"| **Variant** | {variant} |")
        out.append(f"| **Ex-Showroom Price** | **{price}** |")
        if onroad:
            out.append(f"| **Estimated On-Road** | {onroad} |")
        out.append(f"| **Fuel & Powertrain** | {fuel} ({trans}) |")
        if engine:
            out.append(f"| **Engine Capacity** | {engine} |")
        if power:
            out.append(f"| **Power Output** | {power} |")
        if torque:
            out.append(f"| **Torque Output** | {torque} |")
        if mileage:
            out.append(f"| **Efficiency / Range** | {mileage} |")
        out.append(f"| **Safety Rating** | {safety} |")
        out.append("")

        if features:
            out.append("### 📊 Key Vehicle Features")
            for f in features:
                out.append(f"- **{f}**")
            out.append("")

        out.append("### 💡 Buying Guidance & Next Steps")
        out.append(f"- **Quotation:** Contact an authorized {brand} dealership for city-specific RTO taxes and insurance add-ons.")
        out.append(f"- **Test Drive:** Schedule a test drive to evaluate real-world ride comfort and transmission tuning.")

        if consensus.consensus_sources:
            out.append("\n---\n### 🔗 References & Sources\n")
            seen_urls = set()
            count = 1
            for idx, src in enumerate(consensus.consensus_sources[:5], 1):
                out.append(f"{count}. **{src}**")
                count += 1

        return "\n".join(out)
