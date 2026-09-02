"""
Vehicle Search Pipeline Orchestrator — End-to-end execution pipeline connecting all search, filter, scraper, extractor, validator & consensus modules.
"""

import time
from typing import Optional, Dict, Any, Tuple
from app.services.vehicle_search.models.vehicle import ExtractedVehicleData, ConsensusVehicleData
from app.services.vehicle_search.search.query_optimizer import QueryOptimizer
from app.services.vehicle_search.search.duckduckgo import DuckDuckGoSearcher
from app.services.vehicle_search.search.ranking import SearchRanker
from app.services.vehicle_search.filter.duplicate_remover import DuplicateRemover
from app.services.vehicle_search.filter.trusted_domains import TrustedDomainFilter
from app.services.vehicle_search.filter.entity_validator import VehicleEntityValidator
from app.services.vehicle_search.scraper.html_scraper import HTMLScraper
from app.services.vehicle_search.extractor.vehicle_extractor import VehicleExtractor
from app.services.vehicle_search.extractor.price_extractor import PriceExtractor
from app.services.vehicle_search.extractor.specification_extractor import SpecificationExtractor
from app.services.vehicle_search.validator.field_validator import FieldValidator
from app.services.vehicle_search.validator.consensus import ConsensusEngine
from app.services.vehicle_search.llm.formatter import LLMFormatter
from app.services.vehicle_search.utils.logger import log_step


class VehicleSearchOrchestrator:
    """Production-grade Vehicle Search Pipeline Orchestrator with TTL Caching."""

    # In-memory TTL cache: {query_key: (ConsensusVehicleData, timestamp)}
    _CACHE: Dict[str, Tuple[ConsensusVehicleData, float]] = {}
    CACHE_TTL_SECONDS = 3600  # 1 hour cache

    def __init__(self):
        self.optimizer = QueryOptimizer()
        self.searcher = DuckDuckGoSearcher(max_results=15)
        self.ranker = SearchRanker()
        self.duplicate_remover = DuplicateRemover()
        self.domain_filter = TrustedDomainFilter()
        self.entity_validator = VehicleEntityValidator(threshold=0.90)
        self.scraper = HTMLScraper(max_pages=4)
        self.vehicle_extractor = VehicleExtractor()
        self.price_extractor = PriceExtractor()
        self.spec_extractor = SpecificationExtractor()
        self.field_validator = FieldValidator()
        self.consensus_engine = ConsensusEngine()
        self.formatter = LLMFormatter()

    def search_vehicle(self, user_query: str) -> Optional[ConsensusVehicleData]:
        """
        Executes end-to-end pipeline:
        Query -> Check Cache -> Optimize -> Search DDG -> Deduplicate -> Filter Domains -> Validate Entity -> Rank Pages -> Scrape HTML -> Extract Specs -> Validate Fields -> Multi-Source Consensus -> Store Cache.
        """
        if not user_query:
            return None

        cache_key = user_query.strip().lower()
        now = time.time()

        # Check Cache Hit
        if cache_key in self._CACHE:
            cached_data, timestamp = self._CACHE[cache_key]
            if now - timestamp < self.CACHE_TTL_SECONDS:
                log_step("cache", f"CACHE HIT for query: '{user_query}' (age: {int(now - timestamp)}s)")
                return cached_data
            else:
                del self._CACHE[cache_key]

        log_step("pipeline", f"=== STARTING END-TO-END VEHICLE SEARCH PIPELINE FOR: '{user_query}' ===")

        # Step 1: Search Query Optimization
        optimized_query = self.optimizer.optimize(user_query)

        # Step 2: DuckDuckGo Search (15 Results)
        raw_items = self.searcher.search(optimized_query)
        if not raw_items:
            log_step("pipeline", "Step 2 Failed: No search items returned from DuckDuckGo")
            return None

        # Step 3: Remove Duplicate URLs
        unique_items = self.duplicate_remover.remove_duplicates(raw_items)

        # Step 4: Trusted Domain Whitelist Filter
        trusted_items = self.domain_filter.filter(unique_items)
        if not trusted_items:
            log_step("pipeline", "Step 4 Failed: Zero items matched trusted domain whitelist")
            return None

        # Step 5: Multi-Level Entity Validation (Brand, Series, Model, RapidFuzz 90% threshold, model conflict rejection)
        valid_items = self.entity_validator.validate_items(user_query, trusted_items)
        if not valid_items:
            log_step("pipeline", "Step 5 Failed: Zero items passed entity validation")
            return None

        # Step 6: Rank Search Pages
        ranked_items = self.ranker.rank_results(valid_items, user_query)

        # Step 7: Scrape Target HTML Pages & Clean Content
        scraped_pages = self.scraper.scrape_items(ranked_items)
        if not scraped_pages:
            log_step("pipeline", "Step 7 Failed: Failed to scrape HTML text from target pages")
            return None

        # Step 8: Structured Data Extraction & Field Validation
        entity = self.entity_validator.decompose_query(user_query)
        valid_data_list = []

        for page in scraped_pages:
            text = page.get("clean_text", "")
            title = page.get("title", "")
            url = page.get("url", "")
            domain = page.get("domain", "")

            v_info = self.vehicle_extractor.extract_vehicle_info(text, title, user_query)
            p_info = self.price_extractor.extract_prices(text, title)
            s_info = self.spec_extractor.extract_specs(text)

            extracted_data = ExtractedVehicleData(
                brand=v_info["brand"],
                model=v_info["model"],
                series=v_info["series"],
                variant=v_info["variant"],
                fuel=s_info["fuel"],
                transmission=s_info["transmission"],
                engine=s_info["engine"],
                power=s_info["power"],
                torque=s_info["torque"],
                mileage=s_info["mileage"],
                price_ex_showroom=p_info["ex_showroom"],
                price_on_road=p_info["on_road"],
                safety_rating=s_info["safety_rating"],
                features=s_info["features"],
                source_url=url,
                source_domain=domain
            )

            is_valid, reason = self.field_validator.validate_extracted_data(entity, extracted_data)
            if is_valid:
                valid_data_list.append(extracted_data)
            else:
                log_step("field_validator", f"Rejected extracted data from {domain}: {reason}")

        if not valid_data_list:
            log_step("pipeline", "Step 8 Failed: Zero extracted data objects passed field validation rules")
            return None

        # Step 9: Multi-Source Consensus Engine
        consensus_data = self.consensus_engine.determine_consensus(user_query, valid_data_list)

        if consensus_data:
            self._CACHE[cache_key] = (consensus_data, now)

        log_step("pipeline", f"=== PIPELINE COMPLETED SUCCESSFULLY FOR '{user_query}' ===")
        return consensus_data
