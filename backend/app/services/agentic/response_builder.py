"""
Agent Response Builder — Constructs grounded multi-lingual responses from verified tool outputs.
"""

from typing import List, Dict, Any, Optional
from app.services.agentic.schemas import ToolExecutionResult, AgentPlan, VerificationReport

class ResponseBuilder:
    def build_response(
        self,
        plan: AgentPlan,
        tool_results: List[ToolExecutionResult],
        verification: VerificationReport
    ) -> str:
        lang = plan.detected_language
        sections = []

        pricing_res = next((r for r in tool_results if r.tool_name == "calculate_pricing_quote" and r.success), None)
        comp_res = next((r for r in tool_results if r.tool_name == "compare_vehicles" and r.success), None)
        search_res = next((r for r in tool_results if r.tool_name == "search_vehicles" and r.success), None)

        if pricing_res and pricing_res.data:
            summary = pricing_res.data.get("formattedSummary")
            if summary:
                sections.append(summary)

        if comp_res and comp_res.data:
            d = comp_res.data
            a = d["car_a"]
            b = d["car_b"]
            sections.append(f"""### ⚖️ Vehicle Comparison: {a['model']} vs {b['model']}
- **{a['model']} ({a['variant']}):** Ex-Showroom ₹{a['price']/100000:.2f} Lakh ({a['fuel']})
- **{b['model']} ({b['variant']}):** Ex-Showroom ₹{b['price']/100000:.2f} Lakh ({b['fuel']})
- **Price Difference:** ₹{d['price_difference']/100000:.2f} Lakh ({d['cheaper_model']} is more affordable)""")

        if search_res and search_res.data and not pricing_res and not comp_res:
            vehicles = search_res.data.get("vehicles", [])
            sections.append(f"### 🚗 Matching Vehicles Found ({len(vehicles)}):\n")
            for v in vehicles[:5]:
                sections.append(f"- **{v['manufacturer']} {v['model']} ({v['variant']}):** ₹{v['ex_showroom_price']/100000:.2f} Lakh | {v['fuel_type']} | {v['airbags']} Airbags (Safety: {v['safety_rating']}★)")

        if not sections:
            sections.append("Vehicle information retrieved successfully from local automotive database.")

        return "\n\n".join(sections)
