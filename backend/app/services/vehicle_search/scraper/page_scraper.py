"""
Target Page Scraper Module — Scrapes validated trusted pages and strips ads, navigation, headers & footers.
"""

import urllib.request
import urllib.parse
import re
import html
from typing import List, Optional
from app.services.vehicle_search.models import SearchResult, ScrapedPage
from app.services.vehicle_search.utils.logger import log_step

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


class PageScraper:
    """Scrapes clean text content from validated trusted automotive web pages."""

    def __init__(self, timeout: int = 7, max_pages: int = 4):
        self.timeout = timeout
        self.max_pages = max_pages

    def scrape_validated_pages(self, valid_results: List[SearchResult]) -> List[ScrapedPage]:
        if not valid_results:
            return []

        log_step("scraping", f"Scraping up to {self.max_pages} validated trusted pages...")
        scraped_pages: List[ScrapedPage] = []

        for item in valid_results[:self.max_pages]:
            log_step("scraping", f"Scraping content from: {item.url}")
            scraped = self._scrape_url(item.url, item.domain, item.title)
            if scraped:
                scraped_pages.append(scraped)

        log_step("scraping", f"Successfully scraped {len(scraped_pages)} pages out of {len(valid_results[:self.max_pages])}")
        return scraped_pages

    def _scrape_url(self, url: str, domain: str, title: str) -> Optional[ScrapedPage]:
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

            clean_text = self._clean_html(raw_html)

            if len(clean_text) < 100:
                log_step("scraping", f"Skipping {url} (Clean text length too short: {len(clean_text)})")
                return None

            return ScrapedPage(
                url=url,
                domain=domain,
                title=title,
                clean_text=clean_text,
                raw_html=raw_html[:10000]  # Store subset for parsing if needed
            )
        except Exception as e:
            log_step("scraping", f"Scraping failed for {url}: {e}")
            return None

    def _clean_html(self, raw_html: str) -> str:
        """Strips HTML tags, scripts, styles, navigation, headers, footers, and ad containers."""
        if not raw_html:
            return ""

        # Remove script, style, head, nav, footer, header, form, iframe elements
        cleaned = re.sub(r'<(script|style|head|nav|footer|header|form|iframe)[^>]*>.*?</\1>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
        # Remove comments
        cleaned = re.sub(r'<!--.*?-->', '', cleaned, flags=re.DOTALL)
        # Extract text content from tags
        text = re.sub(r'<[^>]+>', ' ', cleaned)
        # Decode HTML entities
        text = html.unescape(text)
        # Normalize whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
