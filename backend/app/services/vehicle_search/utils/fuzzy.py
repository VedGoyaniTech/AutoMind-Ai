"""
Fuzzy Matching Utilities — RapidFuzz with SequenceMatcher fallback
Provides fuzzy string comparison and token ratio matching with customizable thresholds.
"""

import re
import difflib
from typing import Tuple

try:
    from rapidfuzz import fuzz, process
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False


def calculate_similarity_ratio(str1: str, str2: str) -> float:
    """
    Calculate similarity score between 0.0 and 1.0 (or 0 to 100 normalized).
    Uses RapidFuzz token_set_ratio if available, else difflib SequenceMatcher.
    """
    if not str1 or not str2:
        return 0.0

    s1 = str1.lower().strip()
    s2 = str2.lower().strip()

    if s1 == s2:
        return 1.0

    if HAS_RAPIDFUZZ:
        # High-performance token set ratio
        score = fuzz.token_set_ratio(s1, s2) / 100.0
        return score

    # Fallback: token set ratio implementation using difflib
    tokens1 = set(re.findall(r'\w+', s1))
    tokens2 = set(re.findall(r'\w+', s2))

    if not tokens1 or not tokens2:
        return difflib.SequenceMatcher(None, s1, s2).ratio()

    intersection = tokens1.intersection(tokens2)

    # If all tokens of smaller set are in larger set, high match
    min_tokens = min(len(tokens1), len(tokens2))
    if min_tokens > 0 and len(intersection) == min_tokens:
        return 0.95

    # Token overlap ratio
    union = tokens1.union(tokens2)
    jaccard = len(intersection) / len(union) if union else 0.0

    seq_ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
    return max(jaccard, seq_ratio)


def is_entity_match(requested_vehicle: str, page_title: str, threshold: float = 0.90) -> Tuple[bool, float]:
    """
    Validates if requested vehicle name matches the page title or content string.
    Returns (is_match, score). Rejects non-matching vehicles below threshold.
    """
    if not requested_vehicle or not page_title:
        return False, 0.0

    req_clean = requested_vehicle.lower().strip()
    title_clean = page_title.lower().strip()

    # Direct substring inclusion of full requested vehicle tokens
    req_tokens = [w for w in req_clean.split() if len(w) >= 2 and w not in ["price", "cost", "india", "specs", "review", "car"]]
    if req_tokens:
        all_tokens_present = all(t in title_clean for t in req_tokens)
        if all_tokens_present:
            return True, 1.0

    score = calculate_similarity_ratio(req_clean, title_clean)
    is_match = score >= threshold

    return is_match, score
