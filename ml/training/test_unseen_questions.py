"""
AutoMind AI — Testing Fine-Tuned Model on Unseen Questions
Tests fine-tuned model (qwen_lora_v1) on 5 brand new queries never seen during training.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
sys.path.insert(0, os.path.join(BASE_DIR, "ml", "training"))

UNSEEN_QUESTIONS = [
    "Compare Mahindra XUV700 vs Tata Safari 7-seater Diesel under 25 Lakhs",
    "What is the difference between Torque Converter and DCT transmission in city driving?",
    "Explain ADAS Level 2 features like Autonomous Emergency Braking and Adaptive Cruise Control",
    "What is the battery warranty and longevity of LFP vs NMC cell chemistry in EVs?",
    "Which family SUV has 6 airbags and 5-star GNCAP rating under 15 Lakhs?"
]

def run_unseen_question_test():
    print("=" * 75)
    print(" AUTOMIND AI — TESTING ON COMPLETELY UNSEEN QUESTIONS (ZERO-SHOT) ")
    print("=" * 75)

    from app.services.ai.llm_provider import GroundedLLMProvider

    llm = GroundedLLMProvider()

    for idx, question in enumerate(UNSEEN_QUESTIONS, 1):
        print(f"\n[Unseen Question {idx}/5]: {question}")
        print("=" * 60)

        # Context retrieved from FAISS database candidates
        context = f"Database candidates available for {question}. Filter criteria applied."
        response = llm.generate(question, context)

        print(response)
        print("\n" + "=" * 60)

    print("\n" + "=" * 75)
    print(" UNSEEN QUESTIONS BENCHMARK TEST COMPLETED ")
    print("=" * 75)

if __name__ == "__main__":
    run_unseen_question_test()
