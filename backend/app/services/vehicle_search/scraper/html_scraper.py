"""
HTML Scraper Module — Scrapes validated trusted web pages and extracts clean content.
"""

import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from app.services.vehicle_search.scraper.cleaner import ContentCleaner
from app.services.vehicle_search.utils.logger import log_step

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


class HTMLScraper:
    """Scrapes validated trusted web pages via fast HTTP request."""

    def __init__(self, timeout: float = 1.5, max_pages: int = 1):
        self.timeout = timeout
        self.max_pages = max_pages
        self.cleaner = ContentCleaner()

    def scrape_items(self, valid_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not valid_items:
            return []

        log_step("scraping", f"Scraping content from up to {self.max_pages} validated trusted pages...")
        scraped_results = []

        for item in valid_items[:self.max_pages]:
            url = item.get("url", "")
            domain = item.get("domain", "")
            title = item.get("title", "")

            if not url:
                continue

            log_step("scraping", f"Scraping web page: {url}")
            clean_text = self._fetch_and_clean(url)

            if clean_text:
                scraped_results.append({
                    "url": url,
                    "domain": domain,
                    "title": title,
                    "clean_text": clean_text
                })

        log_step("scraping", f"Scraping complete: {len(scraped_results)} web pages successfully scraped")
        return scraped_results

    def _fetch_and_clean(self, url: str) -> Optional[str]:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9"
                }
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type and "xml" not in content_type:
                    return None
                raw_html = response.read().decode("utf-8", errors="ignore")

            clean_text = self.cleaner.clean_html(raw_html)
            if len(clean_text) < 100:
                log_step("scraping", f"Skipping {url} (Extracted text too short: {len(clean_text)})")
                return None

            return clean_text
        except Exception as e:
            log_step("scraping", f"Failed to scrape {url}: {e}")
            return None
