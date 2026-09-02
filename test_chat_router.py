import sys
from app.api.v1.chat import UniversalMessageRouter
from app.services.ai.llm_provider import GroundedLLMProvider

def run_tests():
    router = UniversalMessageRouter()
    llm = GroundedLLMProvider()

    test_cases = [
        # Greetings / Casual
        ("hii", "CASUAL"),
        ("hello", "CASUAL"),
        ("how are you?", "CASUAL"),
        ("thanks", "CASUAL"),
        ("bye", "CASUAL"),
        
        # Question Prefaces
        ("I have a question", "QUESTION_PREFACE"),
        ("can I ask something?", "QUESTION_PREFACE"),
        ("I need your help", "QUESTION_PREFACE"),

        # Real Requests with Prefaces
        ("I have a question: what is ADAS?", "REAL_REQUEST"),
        ("heeyy,i hve so many question , like which car is best like super car, famouse, luxry.!", "REAL_REQUEST"),
        ("hey, which SUV is safest?", "REAL_REQUEST"),

        # Model Comparisons
        ("Tata Nexon EV vs Mahindra XUV400 EV", "REAL_REQUEST"),
        ("Compare Tata Nexon EV and Mahindra XUV400", "REAL_REQUEST"),

        # General non-automotive queries
        ("What is photosynthesis?", "REAL_REQUEST"),
        ("Python vs Java", "REAL_REQUEST"),
        ("Best laptops under 80000", "REAL_REQUEST"),
    ]

    print("=== RUNNING UNIVERSAL ROUTER API UNIT TESTS ===")
    passed = 0
    for query, expected_type in test_cases:
        res = router.route(query)
        actual_type = res["type"]
        status = "PASSED ✅" if actual_type == expected_type else "FAILED ❌"
        if actual_type == expected_type:
            passed += 1
        print(f"[{status}] Query: '{query}' -> Expected: {expected_type} | Got: {actual_type} | Data: {res.get('reply') or res.get('actual_request')}")

    print(f"\nTest Summary: {passed}/{len(test_cases)} Passed.")

    print("\n=== RUNNING ENTITY SAFETY CHECK UNIT TESTS ===")
    comp_prompt = "Tata Nexon EV vs Mahindra XUV400 EV"
    comp_text = "# Tata Nexon EV vs Mahindra XUV400 EV\nModel A = Tata Nexon EV\nModel B = Mahindra XUV400 EV\nModel C = BMW X5"
    sanitized = llm._validate_response_entities(comp_prompt, comp_text)
    print("Before Sanitization contains 'BMW X5':", "BMW X5" in comp_text)
    print("After Sanitization contains 'BMW X5':", "bmw x5" in sanitized.lower())
    if "bmw x5" not in sanitized.lower():
        print("Entity Safety Validation PASSED ✅ (BMW X5 purged successfully!)")
    else:
        print("Entity Safety Validation FAILED ❌")

if __name__ == "__main__":
    run_tests()
