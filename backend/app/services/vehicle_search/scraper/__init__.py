"""
Scraper subpackage init
"""

from app.services.vehicle_search.scraper.html_scraper import HTMLScraper
from app.services.vehicle_search.scraper.cleaner import ContentCleaner

__all__ = ["HTMLScraper", "ContentCleaner"]
