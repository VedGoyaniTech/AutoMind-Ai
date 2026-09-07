import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.car import CarSearchFilter
from app.services.ai.retriever import HybridRetriever
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.services.ai.context_builder import ContextBuilder
from app.services.ai.query_analyzer import QueryAnalyzer
from app.services.ai.embedding_service import embedding_service
from app.services.ingestion.document_parser import DocumentParser
from app.services.ingestion.chunker import RecursiveDocumentChunker
from app.services.ingestion.document_pipeline import DocumentIngestionPipeline
from app.services.ai.llm_provider import get_llm_provider, LocalAutoMindProvider

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def vector_store(tmp_path):
    store_dir = str(tmp_path / "test_vec_store")
    return LocalFAISSVectorStore(index_path=store_dir)

# 1. Exact Filter Retrieval (Budget, Seating, Airbags, Body Type)
def test_1_exact_filter_retrieval(db_session, vector_store):
    analyzer = QueryAnalyzer()
    analysis = analyzer.analyze("Best 7-seater SUV under 25 lakh with 6 airbags")
    
    f_schema: CarSearchFilter = analysis["filter_schema"]
    assert f_schema.price_max == 2500000.0
    assert f_schema.seating_capacity == 7
    assert f_schema.min_airbags == 6
    assert f_schema.body_type == "SUV"

    retriever = HybridRetriever(db_session, vector_store)
    docs, sources, _ = retriever.retrieve("Best 7-seater SUV under 25 lakh with 6 airbags", f_schema)
    assert isinstance(docs, list)
    assert isinstance(sources, list)

# 2. Document Chunk Retrieval
def test_2_knowledge_document_chunk_retrieval(vector_store):
    doc = {
        "title": "CCS2 EV Fast Charging Protocol",
        "text": "Indian electric vehicles use CCS2 standard allowing 50kW DC fast charging from 10% to 80% in 45 minutes.",
        "source_url": "https://automind.ai/docs/ev-charging",
        "source_name": "EV India Guide",
        "document_type": "guide"
    }
    chunker = RecursiveDocumentChunker(chunk_size=500, chunk_overlap=50)
    chunks = chunker.chunk_document(doc, doc_id="doc_ev_1")
    assert len(chunks) == 1
    assert chunks[0]["doc_type"] == "knowledge_chunk"
    assert "doc_hash" in chunks[0]

    embeds = embedding_service.encode([c["text"] for c in chunks])
    vector_store.add_documents(chunks, embeds)

    q_vec = embedding_service.encode("How fast can CCS2 charge an EV?")[0]
    res = vector_store.search(q_vec, top_k=5)
    assert len(res) >= 1
    assert res[0]["doc_type"] == "knowledge_chunk"
    assert "CCS2" in res[0]["text"]

# 3. Generic Chunks Without car_variant_id are NOT Dropped
def test_3_generic_chunks_without_variant_id_preserved(db_session, vector_store):
    doc_chunk = {
        "chunk_id": "rto_bh_c1",
        "document_id": "doc_rto_1",
        "doc_hash": "hash_rto_123",
        "title": "Bharat Series BH Road Tax Rules",
        "text": "BH Series road tax is 8% for cars under 10 lakh, 10% for 10-20 lakh, and 12% for above 20 lakh.",
        "source_url": "https://morth.nic.in/bh-series",
        "source_name": "MoRTH India",
        "document_type": "policy",
        "doc_type": "knowledge_chunk"
    }
    embeds = embedding_service.encode([doc_chunk["text"]])
    vector_store.add_documents([doc_chunk], embeds)

    retriever = HybridRetriever(db_session, vector_store)
    f_schema = CarSearchFilter()
    docs, sources, _ = retriever.retrieve("BH series road tax percentage", f_schema)
    
    # Must contain the knowledge chunk even with NO car_variant_id
    assert len(docs) > 0, f"Docs is empty! Raw docs: {docs}"
    found_chunk = any(d.get("doc_type") == "knowledge_chunk" and "Bharat Series" in d.get("title", "") for d in docs)
    assert found_chunk is True, f"Found chunk is false! Docs: {docs}"

    # Source card should be generated
    assert any("MoRTH" in s.website or "BH" in s.title for s in sources)

# 4. Duplicate Ingestion Prevention via SHA-256 Checksum
def test_4_duplicate_ingestion_prevention(tmp_path, vector_store):
    test_file = tmp_path / "sample_faq.md"
    test_file.write_text("# Battery Warranty FAQ\nAll Tata and MG electric vehicles offer 8 years or 1,60,000 km warranty.")

    pipeline = DocumentIngestionPipeline(vector_store)
    res1 = pipeline.ingest_file(str(test_file), source_name="Warranty Portal")
    assert res1["indexed_chunks"] == 1
    assert res1["skipped_duplicates"] == 0

    # Second ingestion must skip duplicates
    res2 = pipeline.ingest_file(str(test_file), source_name="Warranty Portal")
    assert res2["indexed_chunks"] == 0
    assert res2["skipped_duplicates"] == 1

# 5. Deterministic Non-Random Embeddings
def test_5_deterministic_embeddings():
    text = "Tata Safari 5-Star Bharat NCAP Diesel Automatic"
    vec1 = embedding_service.encode(text)
    vec2 = embedding_service.encode(text)
    assert np.allclose(vec1, vec2, atol=1e-5)
    assert vec1.shape[-1] == 384

# 6. ContextBuilder Evidence Formatting & Evidence IDs
def test_6_context_builder_evidence_formatting():
    cb = ContextBuilder()
    docs = [
        {
            "doc_type": "vehicle_record",
            "manufacturer": "Tata",
            "model": "Safari",
            "variant": "Accomplished Plus",
            "ex_showroom_price": 2450000.0,
            "fuel_type": "Diesel",
            "transmission": "Automatic",
            "seating_capacity": 7,
            "airbags": 7,
            "safety_rating": 5.0,
            "source_info": {"domain": "tatamotors.com"}
        },
        {
            "doc_type": "knowledge_chunk",
            "chunk_id": "c1",
            "title": "Bharat NCAP Safari Test",
            "text": "Tata Safari achieved 5 stars with 30.08 points in Adult Protection.",
            "source_name": "Bharat NCAP",
            "source_url": "https://bncap.in/safari"
        }
    ]
    web = [{"title": "Safari 2024 Review", "snippet": "Best 7-seater SUV safety.", "url": "https://carwale.com", "source": "CarWale"}]
    ctx = cb.build_context(docs=docs, parsed_constraints={"budget": "under 25 lakh", "seats": 7}, web_results=web)

    assert "STRUCTURED VEHICLE FACTS:" in ctx
    assert "[VEH-1] Tata Safari (Accomplished Plus)" in ctx
    assert "RETRIEVED KNOWLEDGE:" in ctx
    assert "[DOC-1] Bharat NCAP Safari Test" in ctx
    assert "TRUSTED LIVE SOURCES:" in ctx
    assert "[WEB-1] Safari 2024 Review" in ctx
    assert "EXTRACTED USER CONSTRAINTS:" in ctx

# 7. No-Answer Behavior When Evidence is Missing
def test_7_no_evidence_honest_response():
    cb = ContextBuilder()
    ctx = cb.build_context(docs=[], parsed_constraints={}, web_results=[])
    assert "No verified automotive records" in ctx

    llm = get_llm_provider()
    resp = llm.generate("1842 steam tractor in Mumbai price", ctx)
    assert "Information not confirmed" in resp or "not confirmed" in resp or "unavailable" in resp.lower()

# 8. Multilingual Query Analysis
def test_8_multilingual_query_analysis():
    analyzer = QueryAnalyzer()
    
    # Hindi
    res_hi = analyzer.analyze("25 लाख के अंदर 7 सीटर डीजल एसयूवी")
    assert res_hi["filter_schema"].price_max == 2500000.0
    assert res_hi["filter_schema"].seating_capacity == 7
    assert res_hi["filter_schema"].fuel_type == "Diesel"
    assert res_hi["filter_schema"].body_type == "SUV"

    # Gujarati
    res_gu = analyzer.analyze("૧૫ લાખ ની અંદર શ્રેષ્ઠ ઇલેક્ટ્રિક કાર")
    assert res_gu["filter_schema"].price_max == 1500000.0
    assert res_gu["filter_schema"].fuel_type == "EV"
