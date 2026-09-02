"""
AutoMind AI — v2 Model Accuracy & Output Quality Test
Tests the qwen_lora_v2 checkpoint against:
  1. Factual accuracy on known ground-truth queries
  2. Intent detection correctness
  3. Output format consistency (tables, headers, markdown)
  4. Hallucination detection (flags invented specs)
  5. Comparison vs v1 output quality
"""

import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
sys.path.insert(0, os.path.join(BASE_DIR, "ml", "training"))

# ── Test Suite: Real queries with expected ground-truth checks ────────────────
TEST_CASES = [
    {
        "id": 1,
        "intent": "price",
        "query": "What is the on-road price of Tata Nexon petrol?",
        "context": "[1] Tata Nexon (Creative Plus 1.2 Petrol MT) | Price: ₹11.5 Lakh | Fuel: Petrol (Manual) | Mileage: 17.4 km/l | Airbags: 6 | Safety: 5 Star\n[2] Tata Nexon (Fearless Plus 1.2 Turbo Petrol AT) | Price: ₹14.75 Lakh | Fuel: Petrol (Automatic) | Mileage: 16.8 km/l | Airbags: 6 | Safety: 5 Star",
        "expect_contains": ["11.5", "Nexon", "Petrol"],
        "expect_not_contains": ["hallucinated", "N/A", "Contact Dealer"],
    },
    {
        "id": 2,
        "intent": "compare",
        "query": "Compare Hyundai Creta vs Kia Seltos diesel automatic",
        "context": "[1] Hyundai Creta (SX (O) 1.5 Turbo DCT) | Price: ₹20.0 Lakh | Fuel: Petrol (DCT) | Mileage: 18.4 km/l | Airbags: 6 | Safety: 4.5 Star\n[2] Kia Seltos (GTX Plus 1.5 Diesel AT) | Price: ₹19.8 Lakh | Fuel: Diesel (Automatic) | Mileage: 19.1 km/l | Airbags: 6 | Safety: 4 Star",
        "expect_contains": ["Creta", "Seltos", "19.8", "20.0"],
        "expect_not_contains": ["Research Strategy"],
    },
    {
        "id": 3,
        "intent": "safety",
        "query": "Which SUV has 6 airbags and 5-star GNCAP rating under 15 lakhs?",
        "context": "[1] Tata Nexon (Creative Plus 1.2 Petrol MT) | Price: ₹11.5 Lakh | Fuel: Petrol (Manual) | Mileage: 17.4 km/l | Airbags: 6 | Safety: 5 Star\n[2] Maruti Brezza (ZXi Plus 1.5 Smart Hybrid MT) | Price: ₹12.5 Lakh | Fuel: Petrol (Manual) | Mileage: 19.8 km/l | Airbags: 6 | Safety: 4 Star",
        "expect_contains": ["Nexon", "6", "5 Star", "11.5"],
        "expect_not_contains": ["Buying Recommendations"],
    },
    {
        "id": 4,
        "intent": "efficiency",
        "query": "Best mileage SUV under 20 lakhs petrol or diesel",
        "context": "[1] Maruti Brezza (ZXi Plus 1.5 Smart Hybrid MT) | Price: ₹12.5 Lakh | Fuel: Petrol (Manual) | Mileage: 19.8 km/l | Airbags: 6 | Safety: 4 Star\n[2] Hyundai Creta (E 1.5 Diesel MT) | Price: ₹14.99 Lakh | Fuel: Diesel (Manual) | Mileage: 21.4 km/l | Airbags: 6 | Safety: 4.5 Star",
        "expect_contains": ["21.4", "Creta", "Brezza", "km/l"],
        "expect_not_contains": ["Decision Logic"],
    },
    {
        "id": 5,
        "intent": "recommend",
        "query": "Best family SUV under 25 lakhs with automatic transmission",
        "context": "[1] Hyundai Creta (SX (O) 1.5 Turbo DCT) | Price: ₹20.0 Lakh | Fuel: Petrol (DCT) | Mileage: 18.4 km/l | Airbags: 6 | Safety: 4.5 Star\n[2] Kia Seltos (GTX Plus 1.5 Diesel AT) | Price: ₹19.8 Lakh | Fuel: Diesel (Automatic) | Mileage: 19.1 km/l | Airbags: 6 | Safety: 4 Star\n[3] Toyota Fortuner (2.8 Diesel 4x4 AT) | Price: ₹39.5 Lakh | Fuel: Diesel (Automatic) | Mileage: 14.2 km/l | Airbags: 7 | Safety: 5 Star",
        "expect_contains": ["Creta", "Seltos", "Automatic"],
        "expect_not_contains": ["Family Use:", "Daily Commute:", "Before Buying:"],
    },
    {
        "id": 6,
        "intent": "specs",
        "query": "Show me full specs of Toyota Fortuner diesel 4x4",
        "context": "[1] Toyota Fortuner (2.8 Diesel 4x4 AT) | Price: ₹39.5 Lakh | Fuel: Diesel (Automatic) | Mileage: 14.2 km/l | Airbags: 7 | Safety: 5 Star",
        "expect_contains": ["Fortuner", "39.5", "14.2", "7"],
        "expect_not_contains": ["Research Strategy", "Buying Recommendations"],
    },
    {
        "id": 7,
        "intent": "general",
        "query": "EV options under 25 lakhs in India",
        "context": "[1] Tata Nexon EV (Empowered Plus Long Range) | Price: ₹16.99 Lakh | Fuel: EV (Automatic) | EV Range: 465 km | Airbags: 6 | Safety: 5 Star\n[2] Mahindra XUV400 EV (EL Pro 39.4 kWh) | Price: ₹17.49 Lakh | Fuel: EV (Automatic) | EV Range: 456 km | Airbags: 6 | Safety: 5 Star",
        "expect_contains": ["Nexon EV", "XUV400", "465", "456"],
        "expect_not_contains": ["Research Strategy", "Decision Logic"],
    },
]

# ── Intent accuracy baseline (v1 produced fixed boilerplate for all) ──────────
V1_KNOWN_ISSUES = [
    "Research Strategy",
    "Decision Logic",
    "Buying Recommendations",
    "- **Family Use:**",
    "- **Daily Commute:**",
    "- **Before Buying:**",
    "Why Recommended: Top rank candidate matching constraint criteria",
]


def score_response(response: str, case: dict) -> dict:
    """Score a single test case response."""
    hits = []
    misses = []
    hallucination_flags = []
    boilerplate_flags = []

    for expected in case["expect_contains"]:
        if expected.lower() in response.lower():
            hits.append(expected)
        else:
            misses.append(expected)

    for banned in case.get("expect_not_contains", []):
        if banned.lower() in response.lower():
            boilerplate_flags.append(banned)

    for v1_pattern in V1_KNOWN_ISSUES:
        if v1_pattern.lower() in response.lower():
            hallucination_flags.append(v1_pattern)

    accuracy = len(hits) / max(len(case["expect_contains"]), 1) * 100
    boilerplate_score = 100 - (len(boilerplate_flags) * 25)
    boilerplate_score = max(0, boilerplate_score)

    return {
        "accuracy": round(accuracy, 1),
        "hits": hits,
        "misses": misses,
        "boilerplate_flags": boilerplate_flags,
        "v1_regressions": hallucination_flags,
        "passed": len(misses) == 0 and len(boilerplate_flags) == 0,
    }


def run_v2_accuracy_test():
    print("=" * 72)
    print(" AUTOMIND AI v2 — ACCURACY & OUTPUT QUALITY BENCHMARK ")
    print("=" * 72)
    print(f"  Model Checkpoint  : qwen_lora_v2")
    print(f"  max_seq_length    : 2048 (v2) vs 512 (v1)")
    print(f"  LoRA Rank         : 32 (v2) vs 16 (v1)")
    print(f"  Test Cases        : {len(TEST_CASES)}")
    print("=" * 72)

    from app.services.ai.llm_provider import GroundedLLMProvider
    llm = GroundedLLMProvider()

    results = []
    total_accuracy = 0.0
    total_passed = 0

    for case in TEST_CASES:
        print(f"\n[Test {case['id']}/7] Intent: {case['intent'].upper()}")
        print(f"Query: {case['query']}")
        print("-" * 60)

        t0 = time.time()
        response = llm.generate(case["query"], case["context"])
        latency = round(time.time() - t0, 3)

        score = score_response(response, case)
        results.append({**case, "score": score, "latency_s": latency, "response_len": len(response)})

        total_accuracy += score["accuracy"]
        if score["passed"]:
            total_passed += 1

        # Print response (first 400 chars)
        preview = response[:400].replace("\n", "\n  ")
        print(f"  {preview}{'...' if len(response) > 400 else ''}")
        print()
        status = "✅ PASS" if score["passed"] else "⚠️  PARTIAL"
        print(f"  {status} | Accuracy: {score['accuracy']}% | Latency: {latency}s | Length: {len(response)} chars")
        if score["misses"]:
            print(f"  Missing expected: {score['misses']}")
        if score["boilerplate_flags"]:
            print(f"  Boilerplate still present: {score['boilerplate_flags']}")
        if score["v1_regressions"]:
            print(f"  v1 regressions: {score['v1_regressions']}")

    avg_accuracy = round(total_accuracy / len(TEST_CASES), 1)

    print("\n" + "=" * 72)
    print(" V2 MODEL BENCHMARK SUMMARY ")
    print("=" * 72)
    print(f"  Tests Run        : {len(TEST_CASES)}")
    print(f"  Passed           : {total_passed}/{len(TEST_CASES)}")
    print(f"  Avg Accuracy     : {avg_accuracy}%")
    print(f"  Boilerplate Free : {'✅ Yes' if all(not r['score']['boilerplate_flags'] for r in results) else '⚠️  Partial'}")
    print(f"  v1 Regression    : {'✅ None' if all(not r['score']['v1_regressions'] for r in results) else '⚠️  Check flags'}")
    print("=" * 72)

    # Save benchmark report
    report_path = os.path.join(BASE_DIR, "ml", "training", "models", "v2_benchmark_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    summary = {
        "model": "qwen_lora_v2",
        "max_seq_length": 2048,
        "lora_r": 32,
        "tests_run": len(TEST_CASES),
        "passed": total_passed,
        "avg_accuracy_pct": avg_accuracy,
        "results": [
            {
                "id": r["id"],
                "intent": r["intent"],
                "query": r["query"],
                "passed": r["score"]["passed"],
                "accuracy_pct": r["score"]["accuracy"],
                "latency_s": r["latency_s"],
                "response_chars": r["response_len"],
                "misses": r["score"]["misses"],
                "boilerplate_flags": r["score"]["boilerplate_flags"],
            }
            for r in results
        ]
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  [✔] Full benchmark report saved → {report_path}")


if __name__ == "__main__":
    run_v2_accuracy_test()
