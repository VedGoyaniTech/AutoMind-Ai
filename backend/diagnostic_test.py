"""
AutoMind AI — Comprehensive Diagnostic & Scenario Test
Run: cd c:\Project-V\backend && python diagnostic_test.py
"""
import sys, os, json, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []

def record(name, passed, detail=""):
    mark = PASS if passed else FAIL
    msg = f"  [{mark}] {name}"
    if detail: msg += f"\n         {detail}"
    print(msg)
    results.append((name, passed, detail))

# ===========================================================================
# SECTION 1: BaseLLMProvider._is_automotive_query FIX
# ===========================================================================
print("\n" + "="*60)
print("  SECTION 1: BaseLLMProvider._is_automotive_query SIGNALS")
print("="*60)
try:
    from app.services.ai.llm_provider import GroundedLLMProvider
    llm = GroundedLLMProvider()

    auto_cases = [
        ("hii",                               False),
        ("hello",                             False),
        ("SUV all show",                      True),
        ("luxury car list",                   True),
        ("me ask the RR mean Rolls Royals",   True),
        ("super car image",                   True),
        ("most famous car list and details",  True),
        ("Tata Nexon EV vs XUV400",           True),
        ("Safest 7-seater cars",              True),
    ]
    for query, expected in auto_cases:
        got = llm._is_automotive_query(query)
        record(f"_is_automotive_query('{query}')", got == expected,
               f"expected={expected} got={got}")
except Exception as e:
    record("_is_automotive_query import", False, traceback.format_exc(limit=2))


# ===========================================================================
# SECTION 2: GroundedLLMProvider.generate() – Tables & Images Verification
# ===========================================================================
print("\n" + "="*60)
print("  SECTION 2: GroundedLLMProvider.generate() TABLE & IMAGE SCENARIOS")
print("="*60)
try:
    from app.services.ai.llm_provider import GroundedLLMProvider
    llm = GroundedLLMProvider()

    SCENARIOS = [
        # (label, msg, context, must_contain_table, must_contain_image)
        ("RR acronym query",         "me ask the RR mean Rolls Royals",   "", True,  False),
        ("Famous cars table query",   "most famous car list and details give", "", True,  False),
        ("Super car image query",     "super car image",                  "", True,  True),
        ("Ferrari image query",       "ferrari photo and specs",          "", True,  True),
        ("SUV list table query",      "SUV all show",                     "", True,  False),
        ("Luxury car list query",     "luxury car list",                  "", True,  False),
        ("EV comparison table query", "Tata Nexon EV vs Mahindra XUV400 EV", "", True, False),
    ]

    for label, msg, ctx, require_table, require_image in SCENARIOS:
        try:
            t0 = time.time()
            result = llm.generate(msg, ctx) or ""
            elapsed = (time.time() - t0) * 1000

            has_table = "| :" in result or "|---" in result or ("|" in result and "\n|" in result)
            has_image = "![" in result and "](" in result

            passed = True
            reasons = []

            if len(result) < 30:
                passed = False
                reasons.append("Length < 30 chars")

            if require_table and not has_table:
                passed = False
                reasons.append("Missing Markdown Table formatting")

            if require_image and not has_image:
                passed = False
                reasons.append("Missing Markdown Image ![alt](url)")

            detail_msg = f"len={len(result)} | table={has_table} | image={has_image} | {elapsed:.0f}ms"
            if reasons:
                detail_msg += " | REASONS: " + ", ".join(reasons)

            record(f"Scenario: '{label}'", passed, detail_msg)
        except Exception as e:
            record(f"Scenario: '{label}'", False, traceback.format_exc(limit=2))

except Exception as e:
    record("GroundedLLMProvider import", False, traceback.format_exc(limit=2))


# ===========================================================================
# SUMMARY
# ===========================================================================
print("\n" + "="*60)
total        = len(results)
passed_count = sum(1 for _, p, _ in results if p)
failed_count = total - passed_count
print(f"  TOTAL: {total}  |  PASSED: {passed_count}  |  FAILED: {failed_count}")
print("="*60)
if failed_count:
    print("\nFAILED TESTS:")
    for name, passed, detail in results:
        if not passed:
            print(f"  ❌ {name}")
            if detail: print(f"     {detail[:300]}")
else:
    print("\n🎉 ALL TABLE & IMAGE SCENARIOS PASSED PERFECTLY!")
