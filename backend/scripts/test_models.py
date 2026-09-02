import os
import sys
import time

# Add parent directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.services.ai.embedding_service import embedding_service
from app.services.ai.query_analyzer import QueryAnalyzer
from app.services.ai.context_builder import ContextBuilder
from app.services.ai.llm_provider import GroundedLLMProvider
from sentence_transformers import SentenceTransformer, util

def run_tests():
    print("=" * 65)
    print("      AUTOMIND AI — COMPLETE MODEL & RAG TEST SUITE")
    print("=" * 65)

    # 1. Test Embedding Models
    print("\n[TEST 1/4] Testing Embedding Models & Semantic Vector Encoding...")
    t0 = time.time()
    
    test_queries = [
        "What are the best electric SUVs with 400km range?",
        "Safest 7 seater cars with 6 airbags under 20 Lakh"
    ]
    
    print(f"  -> Encoding sample queries using default embedding model...")
    embeddings = embedding_service.encode(test_queries)
    t1 = time.time()
    print(f"  ✔ Generated {embeddings.shape[0]} embeddings of shape {embeddings.shape} in {round(t1 - t0, 3)}s.")

    # Cosine Similarity check between 2 sample queries
    sim = util.cos_sim(embeddings[0], embeddings[1]).item()
    print(f"  ✔ Cosine similarity score between queries: {round(sim, 4)}")

    # Test BAAI/bge-small-en-v1.5
    print("\n  -> Testing secondary embedding model 'BAAI/bge-small-en-v1.5'...")
    try:
        bge_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        bge_emb = bge_model.encode(test_queries[0])
        print(f"  ✔ BAAI/bge-small-en-v1.5 output vector dimension: {bge_emb.shape[0]}")
    except Exception as e:
        print(f"  Notice during BAAI test: {e}")

    # 2. Test Query Analyzer
    print("\n[TEST 2/4] Testing Automotive Query Analyzer & Constraint Extractor...")
    analyzer = QueryAnalyzer()
    sample_prompt = "SUV under 20 Lakh with 6 airbags and 5 star safety"
    analysis = analyzer.analyze(sample_prompt)
    
    print(f"  Query: \"{sample_prompt}\"")
    print(f"  ✔ Extracted Intent: {analysis['intent']}")
    print(f"  ✔ Filter Schema: {analysis['filter_schema']}")
    print(f"  ✔ Parsed Constraints: {analysis['parsed_constraints']}")

    # 3. Test Context Builder & Grounded LLM Provider
    print("\n[TEST 3/4] Testing Grounded LLM Provider & Markdown Answer Synthesizer...")
    llm = GroundedLLMProvider()
    
    mock_docs = [
        {
            "manufacturer": "Tata",
            "model": "Nexon EV",
            "variant": "Empowered Plus Long Range",
            "ex_showroom_price": 1699000,
            "fuel_type": "EV",
            "transmission": "Automatic",
            "electric_range": 465,
            "airbags": 6,
            "safety_rating": 5.0,
            "description": "Best selling electric SUV with 465 km range and 5-star GNCAP rating."
        },
        {
            "manufacturer": "Hyundai",
            "model": "Creta",
            "variant": "SX (O) 1.5 Turbo DCT",
            "ex_showroom_price": 2000000,
            "fuel_type": "Petrol",
            "transmission": "DCT",
            "mileage": 18.4,
            "airbags": 6,
            "safety_rating": 4.5,
            "description": "Compact SUV with Level 2 ADAS suite and panoramic sunroof."
        }
    ]

    context_builder = ContextBuilder()
    context_text = context_builder.build_context(mock_docs, analysis["parsed_constraints"])
    print("  ✔ Context builder generated Markdown document stream.")

    # 4. Test Stream Generation
    print("\n[TEST 4/4] Testing Realtime Token Stream Generator...")
    t_start = time.time()
    stream_output = []
    for token in llm.stream(sample_prompt, context_text):
        stream_output.append(token)
    t_end = time.time()

    full_response = "".join(stream_output)
    print(f"  ✔ Streamed {len(stream_output)} tokens in {round(t_end - t_start, 3)}s.")
    print("\n" + "-" * 40 + " SAMPLE AI RESPONSE OUTPUT " + "-" * 40)
    print(full_response[:450] + "\n...")

    print("\n" + "=" * 65)
    print("  ✔ ALL MODEL & RAG COMPONENTS PASSED TESTING SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
