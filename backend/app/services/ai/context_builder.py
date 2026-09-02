import json
from typing import List, Dict, Any

class ContextBuilder:
    """Formats retrieved database documents, validated structured vehicle JSON, and trusted source metadata into prompt context."""

    def build_context(
        self,
        docs: List[Dict[str, Any]],
        parsed_constraints: Dict[str, Any],
        web_results: List[Dict[str, Any]] = None,
        merged_result: Dict[str, Any] = None
    ) -> str:
        lines = []

        if merged_result:
            lines.append("--- VALIDATED STRUCTURED VEHICLE DATA (JSON) ---")
            lines.append(json.dumps(merged_result, indent=2))
            lines.append("--- END VALIDATED STRUCTURED VEHICLE DATA ---\n")

        if docs:
            lines.append("--- RETRIEVED CAR DATABASE CANDIDATES ---")
            for idx, doc in enumerate(docs, 1):
                m_name = doc.get("manufacturer", "")
                model = doc.get("model", "")
                variant = doc.get("variant", "")
                fuel = doc.get("fuel_type", "")
                trans = doc.get("transmission", "")
                mileage = doc.get("mileage")
                range_ev = doc.get("electric_range")
                airbags = doc.get("airbags", 6)
                safety = doc.get("safety_rating")
                src_domain = doc.get("source_info", {}).get("domain", "AutoMind DB") if doc.get("source_info") else "AutoMind DB"

                spec_parts = []
                # price can be a string like "₹12.50 Lakh" or numeric in paisa — handle both
                raw_price = doc.get("ex_showroom_price", "")
                if raw_price and str(raw_price).strip():
                    try:
                        price_numeric = float(str(raw_price).replace(",", "").replace("₹", "").strip())
                        if price_numeric > 1000:
                            # looks like it's in rupees/paisa, convert to lakh
                            price_lakh = round(price_numeric / 100000.0, 2)
                            spec_parts.append(f"Price: ₹{price_lakh} Lakh")
                        else:
                            spec_parts.append(f"Price: ₹{price_numeric} Lakh")
                    except (ValueError, TypeError):
                        # Already a readable string like "₹12.50 Lakh" or "Market Pricing"
                        spec_parts.append(f"Price: {raw_price}")

                spec_parts.append(f"Fuel: {fuel} ({trans})")
                if mileage:
                    spec_parts.append(f"Mileage: {mileage} km/l")
                if range_ev:
                    spec_parts.append(f"EV Range: {range_ev} km")
                spec_parts.append(f"Airbags: {airbags}")
                if safety:
                    spec_parts.append(f"Safety: {safety} Stars")

                spec_summary = " | ".join(spec_parts)
                var_clean = (variant or "").strip()
                mod_clean = (model or "").strip()
                if var_clean and var_clean.lower() not in ["default", "standard", "none", "knowledge record"] and var_clean.lower() not in mod_clean.lower():
                    full_car_name = f"{m_name} {mod_clean} ({var_clean})".strip()
                else:
                    full_car_name = f"{m_name} {mod_clean}".strip()

                lines.append(f"[{idx}] {full_car_name} | {spec_summary} | Source: {src_domain}")

        if web_results:
            lines.append("\n--- TRUSTED WEB SEARCH RESULTS ---")
            for idx, res in enumerate(web_results, 1):
                title = res.get("title", "Web Search Result")
                snippet = res.get("snippet", "")
                url = res.get("url", "")
                src = res.get("source", "DuckDuckGo")
                lines.append(f"[Web {idx}] {title} | {snippet} | Source: {src} ({url})")

        if parsed_constraints:
            active_c = [f"{k}: {v}" for k, v in parsed_constraints.items() if v is not None]
            if active_c:
                lines.append(f"\nUser Query Constraints Extracted: {', '.join(active_c)}")

        if not lines:
            return "No validated vehicle information or web search results could be found for the given query."

        return "\n".join(lines)
