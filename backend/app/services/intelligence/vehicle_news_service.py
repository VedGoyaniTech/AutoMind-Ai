import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import httpx
from app.core.config import settings

logger = logging.getLogger("automind.intelligence.news")

class VehicleNewsService:
    """
    Automotive News Integration via NewsAPI:
    - Queries latest articles by make and model
    - Deduplicates by URL and title
    - Sorts by publication timestamp
    - Never fabricates articles when API returns no results or key is unconfigured.
    """

    def __init__(self):
        self.api_key = settings.NEWSAPI_KEY
        self.base_url = settings.NEWSAPI_BASE_URL.rstrip("/")
        self.timeout = settings.PROVIDER_REQUEST_TIMEOUT_SECONDS

    async def get_car_news(
        self,
        make: str,
        model: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieves recent automotive news articles for the requested make and model.
        """
        if not self.api_key:
            return {
                "status": "not_configured",
                "provider": "NewsAPI",
                "articles": [],
                "count": 0,
                "note": "NEWSAPI_KEY is not configured in environment. Configure key in .env to receive live automotive news.",
                "provenance": "https://newsapi.org/docs"
            }

        query = f'"{make}" AND ("{model}" OR car OR automobile)'
        url = f"{self.base_url}/everything"
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": str(max(10, limit * 2)),
            "language": "en"
        }
        headers = {"X-Api-Key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_articles = data.get("articles", [])
                    cleaned_articles = self._deduplicate_and_clean(raw_articles, limit)
                    return {
                        "status": "live" if cleaned_articles else "empty_results",
                        "provider": "NewsAPI",
                        "count": len(cleaned_articles),
                        "articles": cleaned_articles,
                        "provenance": "https://newsapi.org/docs/endpoints/everything",
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }
                elif resp.status_code in (401, 403):
                    return {
                        "status": "auth_failed",
                        "provider": "NewsAPI",
                        "articles": [],
                        "error": "NewsAPI key is unauthorized or rate-limited.",
                        "provenance": "https://newsapi.org/"
                    }
                elif resp.status_code == 429:
                    return {
                        "status": "rate_limited",
                        "provider": "NewsAPI",
                        "articles": [],
                        "error": "NewsAPI daily developer quota reached.",
                        "provenance": "https://newsapi.org/"
                    }
                else:
                    return {
                        "status": "unavailable",
                        "provider": "NewsAPI",
                        "articles": [],
                        "error": f"NewsAPI returned status {resp.status_code}."
                    }
        except httpx.TimeoutException:
            logger.warning("[VehicleNewsService] NewsAPI request timed out.")
            return {
                "status": "timeout",
                "provider": "NewsAPI",
                "articles": [],
                "error": f"Request to NewsAPI timed out after {self.timeout}s."
            }
        except Exception as e:
            logger.error(f"[VehicleNewsService] NewsAPI error: {e}", exc_info=True)
            return {
                "status": "unavailable",
                "provider": "NewsAPI",
                "articles": [],
                "error": str(e)
            }

    def _deduplicate_and_clean(self, articles: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Deduplicates articles by URL and title, returning the top N items."""
        seen_urls = set()
        seen_titles = set()
        cleaned = []

        for a in articles:
            url = a.get("url") or ""
            title = (a.get("title") or "").strip()
            
            # Skip invalid or [Removed] placeholder articles
            if not title or title == "[Removed]" or not url:
                continue

            clean_title_key = title.lower()[:60]
            if url in seen_urls or clean_title_key in seen_titles:
                continue

            seen_urls.add(url)
            seen_titles.add(clean_title_key)

            source_name = a.get("source", {}).get("name", "Automotive News")
            published_at = a.get("publishedAt")

            cleaned.append({
                "title": title,
                "description": a.get("description") or "",
                "url": url,
                "source": source_name,
                "published_at": published_at,
                "image_url": a.get("urlToImage")
            })

            if len(cleaned) >= limit:
                break

        return cleaned

vehicle_news_service = VehicleNewsService()
