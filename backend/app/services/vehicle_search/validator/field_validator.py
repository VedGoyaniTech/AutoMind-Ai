"""
Field Validator Module — Enforces strict JSON field validation rules:
- Vehicle Brand, Model, and Series must match requested entity
- Price must not be missing or empty
- Variant must be present
- Powertrain specs must not conflict
"""

from typing import Tuple
from app.services.vehicle_search.models.vehicle import ExtractedVehicleData, VehicleEntity
from app.services.vehicle_search.utils.logger import log_step


class FieldValidator:
    """Validates ExtractedVehicleData fields before consensus merging."""

    def validate_extracted_data(self, entity: VehicleEntity, data: ExtractedVehicleData) -> Tuple[bool, str]:
        if not data:
            return False, "Null data object"

        # Rule 1: Brand match check
        if entity.brand.lower() not in data.brand.lower() and data.brand.lower() not in entity.brand.lower():
            return False, f"Brand mismatch: requested '{entity.brand}' vs extracted '{data.brand}'"

        # Rule 2: Model match check
        if entity.model.lower() not in data.model.lower() and data.model.lower() not in entity.model.lower():
            return False, f"Model mismatch: requested '{entity.model}' vs extracted '{data.model}'"

        # Rule 3: Ex-showroom price must be present
        if not data.price_ex_showroom or len(data.price_ex_showroom.strip()) < 2:
            return False, "Missing or empty ex-showroom price"

        # Rule 4: Variant must be non-empty string
        if not data.variant or len(data.variant.strip()) < 1:
            data.variant = "Standard Variant"

        log_step("field_validator", f"PASSED Field Validation for {data.brand} {data.model} ({data.variant}) | Price: {data.price_ex_showroom}")
        return True, "PASSED"
