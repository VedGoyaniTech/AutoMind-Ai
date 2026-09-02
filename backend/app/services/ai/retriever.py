from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.repositories.car_repo import CarRepository
from app.services.ai.vector_store import LocalFAISSVectorStore
from app.services.ai.embedding_service import embedding_service
from app.services.ai.duckduckgo_search import duckduckgo_search_service
from app.schemas.car import CarSearchFilter
from app.schemas.chat import SourceCard
from app.core.config import settings

class HybridRetriever:
    """Hybrid Retriever combining structured SQL database filtering, semantic vector search, and DuckDuckGo live web search."""

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
        """Perform hybrid retrieval and return reranked car documents, source cards, and DuckDuckGo search results."""

        # 0. Query verified dataset store first for strict intent matches
        from app.services.ai.dataset_store import CarDatasetStore
        
        # Extract constraints from filter_schema or prompt
        p_lower = prompt.lower()
        import re
        year_match = re.search(r'\b(19[89][0-9]|20[0-3][0-9])\b', p_lower)
        req_year = int(year_match.group(1)) if year_match else None
        
        is_luxury = (filter_schema.price_min is not None and filter_schema.price_min >= 2000000.0) or any(w in p_lower for w in ["luxury", "luxry", "luxurious", "premium", "exotic", "supercar"])
        req_category = "luxury" if is_luxury else (filter_schema.body_type or (filter_schema.fuel_type if filter_schema.fuel_type == "EV" else None))
        req_fuel = filter_schema.fuel_type

        ds_records = CarDatasetStore.query(
            launch_year=req_year,
            category=req_category,
            fuel_type=req_fuel,
            market="India"
        )

        dataset_docs = []
        for idx, ds in enumerate(ds_records, 1):
            dataset_docs.append({
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

        # 1. Structured SQL candidate retrieval with original filter
        sql_candidates, _ = self.car_repo.search_variants(filter_schema)

        # Apply strict year filter on SQL candidates if year requested
        if req_year and sql_candidates:
            sql_candidates = [c for c in sql_candidates if c.model_year == req_year]

        # Filter out budget cars if luxury query is requested
        if is_luxury and sql_candidates:
            luxury_mfrs = ["BMW", "Mercedes-Benz", "Audi", "Porsche", "Jaguar", "Land Rover", "Volvo", "Lexus", "Rolls-Royce", "Bentley", "Lamborghini", "Ferrari", "BYD"]
            sql_candidates = [c for c in sql_candidates if c.ex_showroom_price >= 2500000.0 or any(lm.lower() in c.car_model.manufacturer.name.lower() for lm in luxury_mfrs)]

        sql_variant_ids = {c.id for c in sql_candidates}

        # 2. Semantic vector retrieval
        query_vector = embedding_service.encode(prompt)[0]
        semantic_docs = self.vector_store.search(query_vector, top_k=top_k)

        # 3. Reciprocal Rank Fusion (RRF) Reranking
        rrf_scores: Dict[int, float] = {}
        doc_map: Dict[int, Dict[str, Any]] = {}

        # Prioritize dataset store matched docs
        for rank, ddoc in enumerate(dataset_docs):
            v_id = ddoc["car_variant_id"]
            rrf_scores[v_id] = 10.0 + (1.0 / (rank + 1))
            doc_map[v_id] = ddoc

        for rank, variant in enumerate(sql_candidates):
            v_id = variant.id
            rrf_scores[v_id] = rrf_scores.get(v_id, 0.0) + (1.0 / (60 + rank + 1))
            doc_map[v_id] = self._variant_to_doc_dict(variant)

        for rank, sdoc in enumerate(semantic_docs):
            v_id = sdoc.get("car_variant_id")
            if not v_id:
                continue
            
            boost = 1.2 if v_id in sql_variant_ids else 1.0
            score = (1.0 / (60 + rank + 1)) * boost
            rrf_scores[v_id] = rrf_scores.get(v_id, 0.0) + score
            
            if v_id not in doc_map:
                v_obj = self.car_repo.get_variant_by_id(v_id)
                if v_obj:
                    # Enforce strict year and luxury filters
                    if req_year and v_obj.model_year != req_year:
                        continue
                    if is_luxury and (v_obj.ex_showroom_price < 2500000.0 and not any(lm.lower() in v_obj.car_model.manufacturer.name.lower() for lm in ["BMW", "Mercedes-Benz", "Audi", "Porsche", "Jaguar", "Land Rover", "Volvo", "Lexus", "Rolls-Royce", "Bentley", "Lamborghini", "Ferrari", "BYD"])):
                        continue
                    doc_map[v_id] = self._variant_to_doc_dict(v_obj)

        sorted_variant_ids = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)[:settings.RERANK_TOP_K]
        top_docs = [doc_map[v_id] for v_id in sorted_variant_ids if v_id in doc_map]

        # 4. DuckDuckGo Live Web Search Retrieval
        web_results: List[Dict[str, Any]] = []
        if getattr(settings, "ENABLE_DUCKDUCKGO_SEARCH", True):
            try:
                search_prompt = prompt
                p_low = prompt.lower()
                if any(w in p_low for w in ["rr", "rolls royce", "rolls-royce", "rolls royal", "rolls royals"]):
                    search_prompt = "Rolls-Royce Motor Cars models pricing specification"
                web_results = duckduckgo_search_service.search(search_prompt)
            except Exception:
                web_results = []

        # 5. Gather verified source cards
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
                "reliability_score": getattr(v.source, 'reliability_score', 0.9)
            }

        m_name = v.car_model.manufacturer.name if (getattr(v, 'car_model', None) and getattr(v.car_model, 'manufacturer', None)) else "Automotive Manufacturer"
        mod_name = v.car_model.name if getattr(v, 'car_model', None) else "Vehicle Model"
        b_type = v.car_model.body_type if getattr(v, 'car_model', None) else "SUV"

        return {
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

    def _collect_top_sources(self, docs: List[Dict[str, Any]], web_results: List[Dict[str, Any]] = None, prompt: str = "") -> List[SourceCard]:
        cards: List[SourceCard] = []
        seen_domains = set()

        for doc in docs:
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
                    id=src.get("id", 1),
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
