"""
DuckDuckGo Search Module — Collects 15 top raw search results.
"""

import urllib.request
import urllib.parse
import json
import re
import html
from typing import List, Dict, Any
from app.services.vehicle_search.utils.logger import log_step

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


class DuckDuckGoSearcher:
    """Executes DuckDuckGo search queries and collects top 15 raw search items."""

    def __init__(self, max_results: int = 15, timeout: float = 2.0):
        self.max_results = max_results
        self.timeout = timeout

    def search(self, query: str) -> List[Dict[str, Any]]:
        if not query:
            return []

        log_step("ddg_search", f"Searching DuckDuckGo for top {self.max_results} results: '{query}'...")
        results = []

        # Strategy 1: Attempt duckduckgo_search library if available
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                items = list(ddgs.text(query, max_results=self.max_results))
                if items:
                    for item in items:
                        t = item.get("title", "")
                        u = item.get("href", item.get("link", ""))
                        s = item.get("body", item.get("snippet", ""))
                        if t and u:
                            results.append({
                                "title": t,
                                "url": u,
                                "snippet": s,
                                "domain": self._extract_domain(u)
                            })
                    log_step("ddg_search", f"Retrieved {len(results)} search items via DDGS library")
                    return results
        except Exception as e:
            log_step("ddg_search", f"DDGS library fallback: {e}")

        # Strategy 2: HTML scraping fallback
        html_items = self._search_html(query)
        if html_items:
            log_step("ddg_search", f"Retrieved {len(html_items)} search items via DDG HTML endpoint")
            return html_items

        log_step("ddg_search", f"No search results returned for '{query}'")
        return []

    def _search_html(self, query: str) -> List[Dict[str, Any]]:
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
            link_matches = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', content, re.DOTALL)
            snippet_matches = re.findall(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', content, re.DOTALL)

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

                domain = self._extract_domain(actual_url)
                if title and actual_url and not actual_url.startswith("//duckduckgo"):
                    url_lower = actual_url.lower()
                    title_lower = title.lower()
                    spam_terms = [
                        "youtube.com/shorts", "youtu.be", "tiktok.com", "instagram.com/reel",
                        "facebook.com/watch", "carryminati", "joshtalks", "rjkarishma", "whatsapp",
                        "#shorts", "comedy", "attitude", "roast", "status", "shorts/"
                    ]
                    if any(st in url_lower or st in title_lower for st in spam_terms):
                        continue

                    results.append({
                        "title": title,
                        "url": actual_url,
                        "snippet": snippet,
                        "domain": domain
                    })

            return results
        except Exception as e:
            log_step("ddg_search", f"HTML search exception: {e}")
            return []

    def _extract_domain(self, url: str) -> str:
        if not url:
            return ""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""
