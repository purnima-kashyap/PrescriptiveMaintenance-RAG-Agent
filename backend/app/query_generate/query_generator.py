from typing import Dict, Any

from app.models.iot_models import IoTAlert


# Optional symptom hints for specific numeric fields, so values also produce
# a human-readable troubleshooting phrase alongside the raw number. Fields
# without an entry here are still included generically as "field_name value".
FIELD_SYMPTOM_RULES = {
    "temperature": [
        (lambda v: v >= 90, "overheating"),
        (lambda v: v <= 0, "cold start low temperature"),
    ],
    "vibration": [
        (lambda v: v >= 7, "excessive vibration"),
    ],
    "pressure": [
        (lambda v: v <= 0, "pressure loss"),
        (lambda v: v >= 100, "overpressure"),
    ],
}


def _get_symptom_terms(field_name: str, value: Any) -> list:
    """Return matching symptom phrases for a field/value, if rules exist for it."""
    terms = []
    if field_name in FIELD_SYMPTOM_RULES and isinstance(value, (int, float)):
        for condition, phrase in FIELD_SYMPTOM_RULES[field_name]:
            if condition(value):
                terms.append(phrase)
    return terms


def generate_query(alert: IoTAlert) -> str:
    """
    Dynamically build a search query from ALL fields present on the alert.
    Works with any current or future IoTAlert schema without modification.
    """
    data: Dict[str, Any] = alert.model_dump()

    query_parts = []
    symptom_terms = []

    if "machine_id" in data:
        query_parts.append(str(data["machine_id"]))
    if "error_code" in data:
        query_parts.append(f"error {data['error_code']}")

    for field_name, value in data.items():
        if field_name in ("machine_id", "error_code"):
            continue

        symptom_terms.extend(_get_symptom_terms(field_name, value))

        if isinstance(value, float):
            query_parts.append(f"{field_name} {value:.0f}")
        else:
            query_parts.append(f"{field_name} {value}")

    query_parts.extend(symptom_terms)
    query_parts.append("troubleshooting")

    return " ".join(query_parts)