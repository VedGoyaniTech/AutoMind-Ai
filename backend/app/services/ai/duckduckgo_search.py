"""
AutoMind AI — DuckDuckGo Web Search Integration Service
Provides real-time web search capabilities using DuckDuckGo to enrich RAG retrieval
with current web facts, pricing, news, and technical automotive specifications.
"""

import logging
import urllib.request
import urllib.parse
import json
import re
import html
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# Preferred trusted automotive & official domains in India
TRUSTED_AUTOMOTIVE_DOMAINS = [
    "autocarindia.com",
    "carwale.com",
    "cardekho.com",
    "zigwheels.com",
    "overdrive.in",
    "auto.hindustantimes.com",
    "timesnownews.com",
    "tatamotors.com",
    "hyundai.com",
    "mahindra.com",
    "marutisuzuki.com",
    "toyotabharat.com",
    "kia.com",
    "skoda-auto.co.in",
    "bmw.in",
    "mercedes-benz.co.in"
]

# In-memory research cache for sub-second retrieval of verified queries
_RESEARCH_CACHE: Dict[str, Dict[str, Any]] = {}

class DuckDuckGoSearchService:
    """
    DuckDuckGo Web Search Service with multi-stage fallback:
    1. duckduckgo_search PyPI library (if available)
    2. DuckDuckGo HTML Web Search endpoint (scraping clean results)
    3. DuckDuckGo Instant Answer JSON API
    4. Domain-focused targeted automotive queries
    """

    def __init__(self, max_results: int = 5, timeout: float = 1.8):
        self.max_results = max_results
        self.timeout = timeout

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute DuckDuckGo web search for the given query.
        Returns list of dicts with keys: 'title', 'snippet', 'url', 'source'.
        """
        if not query or len(query.strip()) < 2:
            return []

        clean_query = query.strip()

        # Strategy 1: Attempt duckduckgo_search library (with thread timeout to prevent hang)
        try:
            from duckduckgo_search import DDGS
            import threading

            results_holder = []
            def _ddgs_search():
                try:
                    with DDGS() as ddgs:
                        results_holder.extend(list(ddgs.text(clean_query, max_results=self.max_results)))
                except Exception:
                    pass

            t = threading.Thread(target=_ddgs_search, daemon=True)
            t.start()
            t.join(timeout=self.timeout)

            if results_holder:
                formatted = []
                for r in results_holder:
                    formatted.append({
                        "title": r.get("title", "DuckDuckGo Result"),
                        "snippet": r.get("body", r.get("snippet", "")),
                        "url": r.get("href", r.get("link", "")),
                        "source": "DuckDuckGo Search"
                    })
                logger.info(f"[DuckDuckGo] Retrieved {len(formatted)} results via DDGS library for query: '{clean_query}'")
                return self._filter_results(formatted)
        except Exception as e:
            logger.debug(f"[DuckDuckGo] DDGS library fallback triggered: {e}")

        # Strategy 2: Query DuckDuckGo HTML endpoint
        html_results = self._search_html(clean_query)
        if html_results:
            logger.info(f"[DuckDuckGo] Retrieved {len(html_results)} results via DDG HTML search for query: '{clean_query}'")
            return self._filter_results(html_results)

        # Strategy 3: Query DuckDuckGo Instant Answer API
        json_results = self._search_api(clean_query)
        if json_results:
            logger.info(f"[DuckDuckGo] Retrieved {len(json_results)} results via DDG API for query: '{clean_query}'")
            return self._filter_results(json_results)

        return []

    def targeted_automotive_search(
        self,
        query: str,
        year: Optional[int] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs targeted domain searches (e.g. site:autocarindia.com, site:carwale.com)
        and caches results with research metadata.
        """
        cache_key = f"{query.lower().strip()}_{year}_{category}_{brand}"
        if cache_key in _RESEARCH_CACHE:
            cached_entry = _RESEARCH_CACHE[cache_key]
            return cached_entry.get("results", [])

        # Build focused search queries
        search_terms = []
        if brand:
            search_terms.append(brand)
        if category:
            search_terms.append(category)
        if year:
            search_terms.append(str(year))
        search_terms.extend(["cars", "India", "launch"])

        search_query = " ".join(search_terms)
        results = self.search(search_query)

        # If broad query returned few results, try preferred domain targeted search
        if len(results) < 2:
            targeted_q = f"site:autocarindia.com {search_query}"
            domain_results = self.search(targeted_q)
            if domain_results:
                results.extend(domain_results)

        # Deduplicate results by URL
        seen_urls = set()
        unique_results = []
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)

        # Cache locally
        _RESEARCH_CACHE[cache_key] = {
            "query": query,
            "year": year,
            "results": unique_results,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "status": "verified" if unique_results else "empty"
        }

        return unique_results

    def _filter_results(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out spam, social media, and low-quality domains."""
        filtered = []
        spam_patterns = [
            "youtube.com/shorts", "youtu.be", "tiktok.com", "instagram.com/reel",
            "facebook.com/watch", "carryminati", "joshtalks", "whatsapp", "reddit.com/r/meme"
        ]

        for item in items:
            url = item.get("url", "").lower()
            title = item.get("title", "").lower()
            if any(sp in url or sp in title for sp in spam_patterns):
                continue
            filtered.append(item)
        return filtered

    def _search_html(self, query: str) -> List[Dict[str, Any]]:
        """Fetch and parse search results from html.duckduckgo.com."""
        try:
            url = "https://html.duckduckgo.com/html/"
            data = urllib.parse.urlencode({"q": query, "b": ""}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://html.duckduckgo.com/"
                }
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content = response.read().decode("utf-8", errors="ignore")

            results = []
            link_matches = re.findall(
                r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                content,
                re.DOTALL
            )
            snippet_matches = re.findall(
                r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
                content,
                re.DOTALL
            )

            for i in range(min(len(link_matches), self.max_results)):
                raw_href, raw_title = link_matches[i]
                raw_snippet = snippet_matches[i] if i < len(snippet_matches) else ""

                title = html.unescape(re.sub(r'<[^>]+>', '', raw_title)).strip()
                snippet = html.unescape(re.sub(r'<[^>]+>', '', raw_snippet)).strip()

                actual_url = raw_href
                if "uddg=" in raw_href:
                    match = re.search(r'uddg=([^&]+)', raw_href)
                    if match:
                        actual_url = urllib.parse.unquote(match.group(1))

                if title and snippet:
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": actual_url,
                        "source": "DuckDuckGo Web"
                    })

            return results
        except Exception as e:
            logger.debug(f"[DuckDuckGo HTML] Exception: {e}")
            return []

    def _search_api(self, query: str) -> List[Dict[str, Any]]:
        """Fetch results from api.duckduckgo.com Instant Answer API."""
        try:
            params = urllib.parse.urlencode({
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            })
            url = f"https://api.duckduckgo.com/?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw_json = response.read().decode("utf-8", errors="ignore")
                data = json.loads(raw_json)

            results = []
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", query),
                    "snippet": data.get("AbstractText"),
                    "url": data.get("AbstractURL", ""),
                    "source": "DuckDuckGo Instant Answer"
                })

            topics = data.get("RelatedTopics", [])
            for topic in topics:
                if len(results) >= self.max_results:
                    break
                text = topic.get("Text")
                first_url = topic.get("FirstURL", "")
                if text:
                    results.append({
                        "title": text[:60] + "...",
                        "snippet": text,
                        "url": first_url,
                        "source": "DuckDuckGo Web"
                    })

            return results
        except Exception as e:
            logger.debug(f"[DuckDuckGo API] Exception: {e}")
            return []

duckduckgo_search_service = DuckDuckGoSearchService()
