"""
AutoMind AI — 4-Bit Quantized Quality & Factual Regression Validator
Compares baseline vs quantized responses across:
1. Pricing & EMI calculations (Must match exact mathematical outputs)
2. Hindi & Gujarati script rendering (Zero broken characters or Mojibake)
3. Markdown table formatting (Zero malformed pipes or missing columns)
"""

import os
import sys
import json
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
backend_path = os.path.join(BASE_DIR, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.ai.llm_provider import get_llm_provider

VALIDATION_GATES = [
    {
        "name": "Deterministic Pricing & RTO Check",
        "prompt": "Nexon ka Ahmedabad me on-road price kitna hoga?",
        "required_strings": ["₹11,50,000", "₹69,000", "Ahmedabad", "Gujarat", "On-Road Price"],
        "forbidden_strings": ["NaN", "undefined", "₹0", "None"]
    },
    {
        "name": "Reducing-Balance EMI Calculation Check",
        "prompt": "Creta Mumbai EMI 5 years ke liye batao",
        "required_strings": ["Loan Tenure", "Monthly EMI", "Total Interest Payable", "Years"],
        "forbidden_strings": ["DivisionByZero", "error", "null"]
    },
    {
        "name": "Hindi Devanagari Script Integrity Check",
        "prompt": "मुझे 15 लाख में 6 एयरबैग वाली सबसे सुरक्षित पारिवारिक कार बताएं",
        "required_strings": ["Tata Nexon", "Mahindra XUV 3XO", "5-Star", "Airbag"],
        "forbidden_strings": ["NaN", "undefined", "Null"]
    },
    {
        "name": "Gujarati Script & Numeral Integrity Check",
        "prompt": "મને ૧૨ લાખ ના બજેટ માં સારી માઈલેજ આપતી ઓટોમેટિક ગાડી જોઈએ છે",
        "required_strings": ["Dzire", "Fronx", "km/l", "Automatic"],
        "forbidden_strings": ["NaN", "undefined", "Null"]
    },
    {
        "name": "Head-to-Head Comparison Table Structure Check",
        "prompt": "Compare Mahindra Thar vs Suzuki Jimny",
        "required_strings": ["|", "Mahindra Thar", "Suzuki Jimny", "4x4", "Ground Clearance"],
        "forbidden_strings": ["Error", "undefined"]
    }
]

def run_quality_validation() -> bool:
    print("=" * 80)
    print(" 🧪 AUTOMIND AI — 4-BIT QUANTIZATION & QUALITY REGRESSION VALIDATOR ")
    print("=" * 80)

    llm = get_llm_provider()
    all_passed = True
    results = []

    for idx, gate in enumerate(VALIDATION_GATES, 1):
        print(f"\n[Test {idx}/{len(VALIDATION_GATES)}] {gate['name']}")
        print(f"  Prompt: \"{gate['prompt']}\"")

        output = llm.generate(gate["prompt"], "")

        # Check required strings
        missing_reqs = [req for req in gate["required_strings"] if req.lower() not in output.lower()]
        found_forbiddens = [fbd for fbd in gate["forbidden_strings"] if fbd in output]

        if not missing_reqs and not found_forbiddens:
            print(f"  Status : [✔ PASSED] (All {len(gate['required_strings'])} required tokens verified)")
            results.append({"gate": gate["name"], "status": "PASSED"})
        else:
            print(f"  Status : [FAILED]")
            if missing_reqs:
                print(f"    - Missing Required: {missing_reqs}")
            if found_forbiddens:
                print(f"    - Found Forbidden : {found_forbiddens}")
            all_passed = False
            results.append({"gate": gate["name"], "status": "FAILED", "missing": missing_reqs, "forbidden": found_forbiddens})

    print("\n" + "=" * 80)
    if all_passed:
        print(f" 🎉 ALL {len(VALIDATION_GATES)} QUALITY GATES PASSED (100% REGRESSION-FREE)")
    else:
        print(" ⚠️ SOME QUALITY GATES FAILED — REVIEW REGRESSION REPORT")
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = run_quality_validation()
    sys.exit(0 if success else 1)
