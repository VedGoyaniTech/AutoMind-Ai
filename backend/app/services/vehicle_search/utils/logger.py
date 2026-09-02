"""
Pipeline Step Logging Utility
"""

import logging

logger = logging.getLogger("vehicle_search_pipeline")
logger.setLevel(logging.INFO)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[VehicleSearchPipeline] %(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def log_step(stage: str, message: str, details: str = ""):
    """Log pipeline execution step."""
    msg = f"[{stage.upper()}] {message}"
    if details:
        msg += f" | {details}"
    logger.info(msg)
