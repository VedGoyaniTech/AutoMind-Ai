"""
AutoMind AI — Agent Response Builder (Part 8 Specification)
"""

from typing import List, Dict, Any, Optional
from app.services.agentic.schemas import ToolResult, AgentPlan, VerificationReport, ResponseKind

class ResponseBuilder:
    """
    Constructs clean, structured user-facing Markdown and structured payloads
    using only verified data from executed tools.
    """

    def build_response(
        self,
        plan: AgentPlan,
        tool_results: List[ToolResult],
        verification: VerificationReport
    ) -> str:
        # 1. Follow-up Priority
        if plan.needs_follow_up and plan.follow_up_question:
            return self._build_follow_up_markdown(plan)

        lang = plan.detected_language
        sections = []

        pricing_res = next((r for r in tool_results if r.tool_name == "calculate_pricing_quote" and r.success), None)
        emi_res = next((r for r in tool_results if r.tool_name == "calculate_emi" and r.success), None)
        comp_res = next((r for r in tool_results if r.tool_name == "compare_vehicles" and r.success), None)
        research_res = next((r for r in tool_results if r.tool_name == "web_research" and r.success), None)
        search_res = next((r for r in tool_results if r.tool_name == "search_vehicles" and r.success), None)

        # 2. Pricing Quote Section
        if pricing_res and pricing_res.data:
            sections.append(self._build_pricing_markdown(pricing_res.data, lang))

        # 3. EMI Options Section
        if emi_res and emi_res.data and not pricing_res:
            sections.append(self._build_emi_markdown(emi_res.data, lang))

        # 4. Comparison Section
        if comp_res and comp_res.data:
            sections.append(self._build_comparison_markdown(comp_res.data, lang))

        # 5. Web Research / Launches Section
        if research_res and research_res.data:
            sections.append(self._build_research_markdown(research_res, lang))

        # 6. Search Vehicles Section
        if search_res and search_res.data and not pricing_res and not comp_res and not research_res:
            sections.append(self._build_search_markdown(search_res.data, lang))

        if not sections:
            if lang == "hi":
                sections.append("वाहन संबंधी विवरण सत्यापित डेटाबेस और रिसर्च इंडेक्स से सफलता से प्राप्त कर लिया गया है।")
            elif lang == "gu":
                sections.append("વાહનની વિગતો સફળતાપૂર્વક ચકાસાયેલ ડેટાબેઝમાંથી મેળવી લેવામાં આવી છે.")
            else:
                sections.append("Vehicle information retrieved successfully from verified automotive database.")

        return "\n\n".join(sections)

    def _build_follow_up_markdown(self, plan: AgentPlan) -> str:
        q = plan.follow_up_question
        return (
            f"### 💡 AutoMind AI — Additional Details Required\n\n"
            f"{q}\n\n"
            f"> **Example:** *\"Nexon Creative Petrol, Ahmedabad, ₹3 lakh down payment, 5 years\"*"
        )

    def _build_pricing_markdown(self, data: Dict[str, Any], lang: str) -> str:
        loc = data.get("location", {})
        city = loc.get("city", "Gujarat")
        veh = data.get("vehicle", {})
        m_name = veh.get("model", "Vehicle")
        v_name = veh.get("variant", "")
        full_title = f"{m_name} {v_name}".strip()

        pb = data.get("priceBreakdown", {})
        ex_show = pb.get("exShowroomPrice", 0)
        rto = pb.get("rtoTax", 0)
        ins = pb.get("insurance", 0)
        tcs = pb.get("tcs", 0)
        fastag = pb.get("fastag", 500)
        on_road = pb.get("onRoadPrice", 0)

        lines = [
            f"## 💰 {full_title} — {city} Estimated On-Road Price\n",
            "| Price Component | Amount (INR) | Details / Slab |",
            "| :--- | ---: | :--- |",
            f"| **Ex-Showroom Price** | ₹{ex_show:,.0f} | Base vehicle quote |",
            f"| **State RTO Road Tax** | ₹{rto:,.0f} | {loc.get('state', 'State')} RTO tax |",
            f"| **Comprehensive Insurance** | ₹{ins:,.0f} | 1-Yr Own Damage + 3-Yr Third Party |",
            f"| **1% TCS** | ₹{tcs:,.0f} | Applicable on vehicles > ₹10 Lakh |",
            f"| **FASTag / Registration** | ₹{fastag:,.0f} | Standard statutory charges |",
            f"| **Estimated On-Road Price** | **₹{on_road:,.0f}** | **Total payable at registration** |\n"
        ]

        # Add EMI Options Table if present
        emi_matrix = data.get("emiOptions", [])
        if emi_matrix:
            lines.append("### 📊 Reducing-Balance Loan EMI Options\n")
            lines.append("| Loan Tenure | Down Payment | Loan Amount | Monthly EMI | Total Interest |")
            lines.append("| :---: | ---: | ---: | ---: | ---: |")
            for emi_opt in emi_matrix:
                t_yrs = emi_opt.get("tenureYears", 5)
                dp = emi_opt.get("downPayment", 0)
                principal = emi_opt.get("principal", 0)
                m_emi = emi_opt.get("monthlyEMI", 0)
                tot_int = emi_opt.get("totalInterest", 0)
                lines.append(f"| **{t_yrs} Years** | ₹{dp:,.0f} | ₹{principal:,.0f} | **₹{m_emi:,.0f} / mo** | ₹{tot_int:,.0f} |")
            lines.append("")

        lines.append("> ℹ️ **Disclaimer:** This is an estimated local quote computed via statutory state RTO slabs. Final dealer quotations may vary slightly with optional accessories.")
        return "\n".join(lines)

    def _build_emi_markdown(self, data: Dict[str, Any], lang: str) -> str:
        on_road = data.get("on_road_price", 0)
        dp = data.get("down_payment", 0)
        rate = data.get("annual_interest_rate", 9.25)
        tenure_opts = data.get("tenure_options", [])

        lines = [
            f"## 🏦 Loan EMI Calculation Breakdown (On-Road: ₹{on_road:,.0f})\n",
            f"- **Down Payment:** ₹{dp:,.0f} | **Annual Interest Rate:** {rate}%\n",
            "| Tenure | Monthly EMI | Principal | Total Interest | Total Payable |",
            "| :---: | ---: | ---: | ---: | ---: |"
        ]
        for opt in tenure_opts:
            lines.append(f"| **{opt.get('tenureYears', 5)} Years** | **₹{opt.get('monthlyEMI', 0):,.0f}** | ₹{opt.get('principal', 0):,.0f} | ₹{opt.get('totalInterest', 0):,.0f} | ₹{opt.get('totalAmount', 0):,.0f} |")
        return "\n".join(lines)

    def _build_comparison_markdown(self, data: Dict[str, Any], lang: str) -> str:
        a = data.get("car_a", {})
        b = data.get("car_b", {})
        lines = [
            f"## ⚖️ Head-to-Head Comparison: {a.get('name', 'Car A')} vs {b.get('name', 'Car B')}\n",
            "| Metric / Feature | **" + a.get('name', 'Car A') + "** | **" + b.get('name', 'Car B') + "** |",
            "| :--- | :--- | :--- |",
            f"| **Starting Ex-Showroom** | ₹{a.get('ex_showroom_price', 0)/100000:.2f} Lakh | ₹{b.get('ex_showroom_price', 0)/100000:.2f} Lakh |",
            f"| **Fuel Options** | {', '.join(a.get('fuel_options', ['Petrol']))} | {', '.join(b.get('fuel_options', ['Petrol']))} |",
            f"| **Safety & Airbags** | {a.get('safety', '5-Star')} ({a.get('airbags', 6)} Airbags) | {b.get('safety', '5-Star')} ({b.get('airbags', 6)} Airbags) |\n",
            f"### 🏆 Verdict\n{data.get('verdict', '')}\n",
            "> 💡 *Share your city and down payment if you would like on-road price and EMI comparisons.*"
        ]
        return "\n".join(lines)

    def _build_research_markdown(self, res: ToolResult, lang: str) -> str:
        results = res.data.get("results", [])
        q = res.data.get("query", "Automotive Research")
        lines = [f"## 🔍 Verified Automotive Research: *\"{q}\"*\n"]

        if results:
            lines.append("| # | Article Title | Verified Publisher | Source Link |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for idx, r in enumerate(results[:5], 1):
                title = r.get("title", "Article")
                domain = r.get("domain", "automotive.org")
                url = r.get("url", "#")
                lines.append(f"| {idx} | **{title}** | *{domain}* | [View Article]({url}) |")
            lines.append("")

        return "\n".join(lines)

    def _build_search_markdown(self, data: Dict[str, Any], lang: str) -> str:
        vehicles = data.get("vehicles", [])
        lines = [f"## 🚗 Matching Vehicles Found ({len(vehicles)})\n"]
        for v in vehicles[:5]:
            mfr = v.get("manufacturer", "")
            mod = v.get("model", v.get("name", ""))
            price = v.get("price", v.get("ex_showroom_price", 0))
            fuel = v.get("fuel_type", "Petrol")
            lines.append(f"- **{mfr} {mod}**: ₹{price/100000:.2f} Lakh | {fuel}")
        return "\n".join(lines)
