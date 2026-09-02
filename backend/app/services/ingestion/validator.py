from typing import Dict, Any, Tuple, Optional

class DataValidator:
    """Validates raw automotive dataset fields prior to database insertion."""

    REQUIRED_FIELDS = ["manufacturer", "model", "variant", "ex_showroom_price", "fuel_type"]

    @classmethod
    def validate_record(cls, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        for field in cls.REQUIRED_FIELDS:
            val = record.get(field)
            if val is None or str(val).strip() == "":
                return False, f"Missing required field: '{field}'"

        try:
            price = float(record.get("ex_showroom_price", 0))
            if price <= 0:
                return False, "Ex-showroom price must be positive."
        except (ValueError, TypeError):
            return False, "Invalid numerical format for ex_showroom_price."

        return True, None
