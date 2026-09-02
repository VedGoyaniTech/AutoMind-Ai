"""
Content Cleaner Module — Strips HTML navigation, headers, footers, sidebars, ads, recommended cars & SEO titles.
"""

import re
import html
from app.services.vehicle_search.utils.logger import log_step


class ContentCleaner:
    """Cleans scraped raw HTML into clean, noise-free body text."""

    SEO_TITLE_PATTERNS = [
        r'.*?Price\s*-\s*Images,?\s*Colors\s*&\s*Reviews.*?',
        r'.*?Price,\s*Images,\s*Specs\s*&\s*Reviews.*?',
        r'.*?Launched at Just.*?',
        r'.*?Relaunched - India\'s Cheapest.*?',
        r'.*?CarWale.*?',
        r'.*?CarDekho.*?',
        r'.*?ZigWheels.*?'
    ]

    def clean_html(self, raw_html: str) -> str:
        if not raw_html:
            return ""

        # Remove script, style, head, nav, footer, header, form, iframe, sidebar, ad containers
        cleaned = re.sub(r'<(script|style|head|nav|footer|header|form|iframe|aside)[^>]*>.*?</\1>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML comments
        cleaned = re.sub(r'<!--.*?-->', '', cleaned, flags=re.DOTALL)
        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', cleaned)
        # Decode HTML entities
        text = html.unescape(text)
        # Normalize lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        filtered_lines = []

        for line in lines:
            # Skip SEO title banners
            is_seo_title = any(re.match(p, line, re.IGNORECASE) for p in self.SEO_TITLE_PATTERNS)
            if not is_seo_title:
                filtered_lines.append(line)

        return "\n".join(filtered_lines)
