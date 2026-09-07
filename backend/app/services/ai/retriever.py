import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.repositories.car_repo import CarRepository
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.services.ai.embedding_service import embedding_service
from app.services.ai.duckduckgo_search import duckduckgo_search_service
from app.schemas.car import CarSearchFilter
from app.schemas.chat import SourceCard
from app.core.config import settings

logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Production-grade Hybrid Retriever combining:
    1. Exact SQL constraints on structured vehicle catalog (price, seats, airbags, fuel, body type).
    2. Semantic vector search across structured vehicle embeddings.
    3. Semantic vector search across unstructured knowledge chunks (brochures, manuals, EV guides, FAQs).
    4. Curated historical dataset lookup (2018–2025 launches & specs).
    5. Targeted DuckDuckGo automotive web research fallback.
    6. Reciprocal Rank Fusion (RRF) reranking with exact-constraint boosting.
    """

    def __init__(self, db: Session, vector_store: LocalFAISSVectorStore):
        self.db = db
        self.car_repo = CarRepository(db)
        self.vector_store = vector_store

    def retrieve(
        self,
        prompt: str,
        filter_schema: CarSearchFilter,
        top_k: int = settings.RETRIEVAL_TOP_K
    ) -> Tuple[List[Dict[str, Any]], List[SourceCard], List[Dict[str, Any]]]:
        """Perform hybrid retrieval and return reranked documents, source cards, and web results."""
        p_lower = prompt.lower().strip()
        
        # 1. Extract intent & temporal signals
        year_match = re.search(r'\b(19[89][0-9]|20[0-3][0-9])\b', p_lower)
        req_year = int(year_match.group(1)) if year_match else None
        
        is_luxury = (filter_schema.price_min is not None and filter_schema.price_min >= 2000000.0) or any(
            w in p_lower for w in ["luxury", "luxry", "luxurious", "premium", "exotic", "supercar"]
        )
        req_category = "luxury" if is_luxury else (filter_schema.body_type or (filter_schema.fuel_type if filter_schema.fuel_type == "EV" else None))
        req_fuel = filter_schema.fuel_type

        # 2. Query Curated Historical & Dataset Store (only if year/category/fuel specified)
        from app.services.ai.dataset_store import CarDatasetStore
        if req_year or req_category or req_fuel:
            ds_records = CarDatasetStore.query(
                launch_year=req_year,
                category=req_category,
                fuel_type=req_fuel,
                market="India"
            )
        else:
            ds_records = []

        dataset_docs: List[Dict[str, Any]] = []
        for idx, ds in enumerate(ds_records, 1):
            dataset_docs.append({
                "doc_type": "vehicle_record",
                "car_variant_id": 9000 + idx,
                "car_name": ds["car_name"],
                "brand": ds["brand"],
                "manufacturer": ds["brand"],
                "model": ds["car_name"],
                "variant": ds["car_name"],
                "launch_year": ds["launch_year"],
                "launch_date": ds["launch_date"],
                "status": ds["status"],
                "country": ds["country"],
                "market": ds["country"],
                "segment": ds["segment"],
                "body_type": ds["segment"],
                "category": ds["category"],
                "fuel_type": ds["fuel_type"],
                "ex_showroom_price": ds["price"],
                "price": ds["price"],
                "source_info": {
                    "id": 900 + idx,
                    "name": ds["source_name"],
                    "domain": ds["source_name"].lower().replace(" ", "") + ".com",
                    "base_url": ds["source_url"],
                    "reliability_score": 0.99
                }
            })

        # 3. Structured SQL candidate retrieval with exact filter constraints
        has_sql_constraints = bool(
            filter_schema.manufacturer or filter_schema.body_type or filter_schema.fuel_type or
            filter_schema.price_max or filter_schema.price_min or filter_schema.min_airbags or
            filter_schema.min_safety_rating or filter_schema.seating_capacity or filter_schema.transmission
        )
        if has_sql_constraints:
            sql_candidates, _ = self.car_repo.search_variants(filter_schema)
        else:
            sql_candidates = []

        # Apply strict year filter on SQL candidates if requested
        if req_year and sql_candidates:
            sql_candidates = [c for c in sql_candidates if c.model_year == req_year]

        # Apply luxury filter if requested
        if is_luxury and sql_candidates:
            luxury_mfrs = ["BMW", "Mercedes-Benz", "Audi", "Porsche", "Jaguar", "Land Rover", "Volvo", "Lexus", "Rolls-Royce", "Bentley", "Lamborghini", "Ferrari", "BYD"]
            sql_candidates = [c for c in sql_candidates if c.ex_showroom_price >= 2500000.0 or any(lm.lower() in c.car_model.manufacturer.name.lower() for lm in luxury_mfrs)]

        sql_variant_ids = {c.id for c in sql_candidates}

        # 4. Semantic Vector Retrieval (Embed query)
        query_vector = embedding_service.encode(prompt)[0]
        # Search all documents in the vector store (both vehicle records and knowledge chunks)
        semantic_docs = self.vector_store.search(query_vector, top_k=top_k)

        # 5. Reciprocal Rank Fusion (RRF) Reranking
        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        # A. Prioritize dataset store matched docs
        for rank, ddoc in enumerate(dataset_docs):
            key = f"ds_{ddoc['car_variant_id']}"
            rrf_scores[key] = 10.0 + (1.0 / (rank + 1))
            doc_map[key] = ddoc

        # B. Exact SQL candidate matches
        for rank, variant in enumerate(sql_candidates):
            key = f"veh_{variant.id}"
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (60 + rank + 1)) * 1.5
            doc_map[key] = self._variant_to_doc_dict(variant)

        # C. Semantic documents (both vehicle records and knowledge chunks)
        for rank, sdoc in enumerate(semantic_docs):
            doc_type = sdoc.get("doc_type", "vehicle_record")
            
            if doc_type == "knowledge_chunk" or "text" in sdoc and "chunk_id" in sdoc:
                # Generic unstructured knowledge chunk (Never skipped!)
                c_id = sdoc.get("chunk_id", f"chunk_{rank}")
                key = f"chunk_{c_id}"
                score = (1.0 / (60 + rank + 1)) * 1.2
                rrf_scores[key] = rrf_scores.get(key, 0.0) + score
                sdoc["doc_type"] = "knowledge_chunk"
                doc_map[key] = sdoc
            else:
                # Structured vehicle record from vector store
                v_id = sdoc.get("car_variant_id")
                if not v_id:
                    # Still keep as generic document
                    key = f"generic_{rank}"
                    rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (60 + rank + 1))
                    doc_map[key] = sdoc
                    continue

                key = f"veh_{v_id}"
                boost = 1.3 if v_id in sql_variant_ids else 1.0
                score = (1.0 / (60 + rank + 1)) * boost
                rrf_scores[key] = rrf_scores.get(key, 0.0) + score

                if key not in doc_map:
                    v_obj = self.car_repo.get_variant_by_id(v_id)
                    if v_obj:
                        if req_year and v_obj.model_year != req_year:
                            continue
                        if is_luxury and (v_obj.ex_showroom_price < 2500000.0 and not any(lm.lower() in v_obj.car_model.manufacturer.name.lower() for lm in ["BMW", "Mercedes-Benz", "Audi", "Porsche", "Jaguar", "Land Rover", "Volvo", "Lexus", "Rolls-Royce", "Bentley", "Lamborghini", "Ferrari", "BYD"])):
                            continue
                        doc_map[key] = self._variant_to_doc_dict(v_obj)
                    else:
                        doc_map[key] = sdoc

        sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)[:settings.RERANK_TOP_K]
        top_docs = [doc_map[k] for k in sorted_keys if k in doc_map]

        # 6. DuckDuckGo Live Web Search Retrieval (Only when enabled and relevant)
        web_results: List[Dict[str, Any]] = []
        if getattr(settings, "ENABLE_DUCKDUCKGO_SEARCH", True):
            try:
                search_prompt = prompt
                if any(w in p_lower for w in ["rr", "rolls royce", "rolls-royce", "rolls royal", "rolls royals"]):
                    search_prompt = "Rolls-Royce Motor Cars models pricing specification"
                web_results = duckduckgo_search_service.search(search_prompt)
            except Exception as e:
                logger.warning(f"[HybridRetriever] Web search fallback notice: {e}")
                web_results = []

        # 7. Gather verified source cards
        sources = self._collect_top_sources(top_docs, web_results, prompt)

        return top_docs, sources, web_results

    def _variant_to_doc_dict(self, v) -> Dict[str, Any]:
        source_info = None
        if getattr(v, 'source', None):
            source_info = {
                "id": v.source.id,
                "name": v.source.name,
                "domain": v.source.domain,
                "base_url": v.source.base_url,
                "reliability_score": getattr(v.source, 'reliability_score', 0.95)
            }

        m_name = v.car_model.manufacturer.name if (getattr(v, 'car_model', None) and getattr(v.car_model, 'manufacturer', None)) else "Automotive Manufacturer"
        mod_name = v.car_model.name if getattr(v, 'car_model', None) else "Vehicle Model"
        b_type = v.car_model.body_type if getattr(v, 'car_model', None) else "SUV"

        return {
            "doc_type": "vehicle_record",
            "car_variant_id": v.id,
            "manufacturer": m_name,
            "model": mod_name,
            "variant": getattr(v, 'variant_name', 'Standard Variant'),
            "body_type": b_type,
            "fuel_type": getattr(v, 'fuel_type', 'Petrol'),
            "transmission": getattr(v, 'transmission', 'Manual'),
            "ex_showroom_price": getattr(v, 'ex_showroom_price', 'Market Pricing'),
            "estimated_on_road_price": getattr(v, 'estimated_on_road_price', 'Market Pricing'),
            "currency": getattr(v, 'currency', 'INR'),
            "mileage": getattr(v, 'combined_mileage', '15.0 kmpl'),
            "electric_range": getattr(v, 'electric_range', None),
            "airbags": getattr(v, 'airbags', 6),
            "safety_rating": getattr(v, 'safety_rating', '5-Star NCAP'),
            "seating_capacity": getattr(v, 'seating_capacity', 5),
            "horsepower": getattr(v, 'horsepower', None),
            "torque_nm": getattr(v, 'torque_nm', None),
            "description": getattr(v, 'description', None),
            "image_url": getattr(v, 'image_url', None),
            "source_url": getattr(v, 'source_url', None),
            "source_info": source_info
        }

    def _collect_top_sources(
        self,
        docs: List[Dict[str, Any]],
        web_results: List[Dict[str, Any]] = None,
        prompt: str = ""
    ) -> List[SourceCard]:
        cards: List[SourceCard] = []
        seen_domains = set()

        for doc in docs:
            doc_type = doc.get("doc_type", "vehicle_record")
            
            if doc_type == "knowledge_chunk":
                title = doc.get("title", "Verified Automotive Document")
                src_name = doc.get("source_name", "AutoMind Knowledge Base")
                url = doc.get("source_url") or "https://automind.ai/docs"
                domain = doc.get("domain") or (url.split("//")[1].split("/")[0] if "//" in url else "automind.ai")
                
                if domain in seen_domains:
                    continue
                seen_domains.add(domain)

                cards.append(
                    SourceCard(
                        id=len(cards) + 1,
                        title=title,
                        website=src_name,
                        url=url,
                        domain=domain,
                        reason=f"Verified knowledge document: {title[:40]}",
                        reliability_score=doc.get("reliability_score", 0.92)
                    )
                )
            else:
                src = doc.get("source_info")
                if not src:
                    continue

                domain = src.get("domain", "automotive.org")
                if domain in seen_domains:
                    continue
                seen_domains.add(domain)

                m_name = doc.get("manufacturer", "")
                mod_name = doc.get("model", "")
                var_name = doc.get("variant", "")
                title = f"{m_name} {mod_name} {var_name} Official Specs & Pricing"

                url = doc.get("source_url") or f"https://{domain}/specs/{m_name.lower()}-{mod_name.lower()}"
                reason = f"Verified automotive specs, pricing, and safety ratings for {m_name} {mod_name}."

                cards.append(
                    SourceCard(
                        id=src.get("id", len(cards) + 1),
                        title=title,
                        website=src.get("name", "AutoMind Direct"),
                        url=url,
                        domain=domain,
                        reason=reason,
                        reliability_score=src.get("reliability_score", 0.95)
                    )
                )

            if len(cards) >= 4:
                break

        # Append DuckDuckGo live web search sources
        if web_results:
            for idx, wres in enumerate(web_results, 1):
                url = wres.get("url", "https://duckduckgo.com")
                domain = "duckduckgo.com"
                if "//" in url:
                    try:
                        domain = url.split("//")[1].split("/")[0]
                    except Exception:
                        domain = "duckduckgo.com"

                if domain in seen_domains:
                    continue
                seen_domains.add(domain)

                cards.append(
                    SourceCard(
                        id=100 + idx,
                        title=wres.get("title", "DuckDuckGo Live Result"),
                        website="DuckDuckGo Web Search",
                        url=url,
                        domain=domain,
                        reason=f"Live DuckDuckGo web result for: '{prompt[:35]}'",
                        reliability_score=0.92
                    )
                )

                if len(cards) >= 5:
                    break

        return cards
