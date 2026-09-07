import json
from typing import List, Dict, Any, Optional
from app.core.config import settings

class ContextBuilder:
    """
    Constructs a concise, citation-indexed prompt context for the LLM.
    Separates:
    1. STRUCTURED VEHICLE FACTS ([VEH-N])
    2. RETRIEVED KNOWLEDGE ([DOC-N])
    3. TRUSTED LIVE SOURCES ([WEB-N])
    """

    def build_context(
        self,
        docs: List[Dict[str, Any]],
        parsed_constraints: Dict[str, Any],
        web_results: List[Dict[str, Any]] = None,
        merged_result: Dict[str, Any] = None,
        max_docs: int = settings.MAX_CONTEXT_DOCUMENTS
    ) -> str:
        sections = []

        # 1. Merged structured vehicle record (if direct single-car search matched)
        if merged_result:
            sections.append("STRUCTURED VEHICLE SPECIFICATION (EXACT MATCH):\n" + json.dumps(merged_result, indent=2))

        # 2. Separate vehicle records from knowledge chunks
        veh_records = []
        knowledge_chunks = []

        for d in docs:
            d_type = d.get("doc_type", "vehicle_record")
            if d_type == "knowledge_chunk" or ("text" in d and "chunk_id" in d):
                knowledge_chunks.append(d)
            else:
                veh_records.append(d)

        # 3. Format STRUCTURED VEHICLE FACTS
        if veh_records:
            veh_lines = ["STRUCTURED VEHICLE FACTS:"]
            for idx, doc in enumerate(veh_records[:max_docs], 1):
                m_name = doc.get("manufacturer", "")
                model = doc.get("model", "")
                variant = doc.get("variant", "")
                fuel = doc.get("fuel_type", "")
                trans = doc.get("transmission", "")
                mileage = doc.get("mileage")
                range_ev = doc.get("electric_range")
                airbags = doc.get("airbags", 6)
                safety = doc.get("safety_rating")
                seats = doc.get("seating_capacity")
                src_domain = doc.get("source_info", {}).get("domain", "AutoMind DB") if doc.get("source_info") else "AutoMind DB"

                spec_parts = []
                raw_price = doc.get("ex_showroom_price", "")
                if raw_price and str(raw_price).strip():
                    try:
                        price_num = float(str(raw_price).replace(",", "").replace("₹", "").strip())
                        if price_num > 1000:
                            spec_parts.append(f"Price: ₹{round(price_num / 100000.0, 2)} Lakh")
                        else:
                            spec_parts.append(f"Price: ₹{price_num} Lakh")
                    except (ValueError, TypeError):
                        spec_parts.append(f"Price: {raw_price}")

                if fuel:
                    spec_parts.append(f"Fuel: {fuel} ({trans or 'Standard'})")
                if seats:
                    spec_parts.append(f"Seats: {seats}")
                if airbags:
                    spec_parts.append(f"Airbags: {airbags}")
                if safety:
                    spec_parts.append(f"Safety: {safety}")
                if mileage:
                    spec_parts.append(f"Mileage: {mileage}")
                if range_ev:
                    spec_parts.append(f"EV Range: {range_ev} km")

                spec_summary = " | ".join(spec_parts)
                var_clean = (variant or "").strip()
                mod_clean = (model or "").strip()
                if var_clean and var_clean.lower() not in ["default", "standard", "none", "knowledge record"] and var_clean.lower() not in mod_clean.lower():
                    full_car_name = f"{m_name} {mod_clean} ({var_clean})".strip()
                else:
                    full_car_name = f"{m_name} {mod_clean}".strip()

                veh_lines.append(f"[VEH-{idx}] {full_car_name} | {spec_summary} | Source: {src_domain}")
            sections.append("\n".join(veh_lines))

        # 4. Format RETRIEVED KNOWLEDGE
        if knowledge_chunks:
            chunk_lines = ["RETRIEVED KNOWLEDGE:"]
            for idx, chunk in enumerate(knowledge_chunks[:max_docs], 1):
                title = chunk.get("title", "Automotive Document")
                text = chunk.get("text", "").replace("\n", " ").strip()
                src_name = chunk.get("source_name", "AutoMind Knowledge Base")
                src_url = chunk.get("source_url", "")
                chunk_lines.append(f"[DOC-{idx}] {title} | {text[:350]}... | Source: {src_name} ({src_url})")
            sections.append("\n".join(chunk_lines))

        # 5. Format TRUSTED LIVE SOURCES (DuckDuckGo)
        if web_results:
            web_lines = ["TRUSTED LIVE SOURCES:"]
            for idx, res in enumerate(web_results[:5], 1):
                title = res.get("title", "Live Search Result")
                snippet = res.get("snippet", "").replace("\n", " ").strip()
                url = res.get("url", "")
                src = res.get("source", "DuckDuckGo")
                web_lines.append(f"[WEB-{idx}] {title} | {snippet} | Source: {src} ({url})")
            sections.append("\n".join(web_lines))

        # 6. Extracted Query Constraints Summary
        if parsed_constraints:
            active_c = [f"{k}: {v}" for k, v in parsed_constraints.items() if v is not None]
            if active_c:
                sections.append(f"EXTRACTED USER CONSTRAINTS: {', '.join(active_c)}")

        if not sections:
            return "No verified automotive records, knowledge documents, or web sources found."

        return "\n\n".join(sections)
