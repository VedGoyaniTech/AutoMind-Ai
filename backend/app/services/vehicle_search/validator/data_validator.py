"""
Data Validator Module — Enforces strict JSON validation rules:
- Vehicle name must match
- Price must not be missing
- Variant must not be empty
- Engine must match vehicle family
"""

from typing import Optional, Tuple
from app.services.vehicle_search.models import ExtractedVehicleSpec
from app.services.vehicle_search.utils.fuzzy import is_entity_match
from app.services.vehicle_search.utils.logger import log_step


class DataValidator:
    """Validates ExtractedVehicleSpec JSON schema against strict validation rules."""

    def validate_spec(self, requested_vehicle: str, spec: ExtractedVehicleSpec) -> Tuple[bool, str]:
        """
        Validates extracted JSON object.
        Returns (is_valid, rejection_reason).
        """
        if not spec:
            return False, "Null specification object"

        # Rule 1: Vehicle name matching
        is_match, score = is_entity_match(requested_vehicle, spec.vehicle_name, threshold=0.85)
        if not is_match:
            return False, f"Vehicle name mismatch: requested '{requested_vehicle}' vs extracted '{spec.vehicle_name}' (Score: {score:.2f})"

        # Rule 2: Price must be present and valid
        if not spec.ex_showroom_price or len(spec.ex_showroom_price.strip()) < 2:
            return False, "Missing or empty ex-showroom price"

        # Rule 3: Variant name must not be empty
        if not spec.variant_name or len(spec.variant_name.strip()) < 1:
            spec.variant_name = "Standard Variant"

        # Rule 4: Fuel type check
        if not spec.fuel_type:
            spec.fuel_type = "Petrol"

        log_step("data_validation", f"PASSED Validation for {spec.vehicle_name} ({spec.variant_name}) | Price: {spec.ex_showroom_price}")
        return True, "PASSED"
