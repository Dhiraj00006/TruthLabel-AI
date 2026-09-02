"""Tier-3 advisory check for unsubstantiated marketing claims.

Pattern-based in v1 (no LLM call yet). Output is always tier 3_advisory and must
never be merged into compliance verdicts (tiers 1-2) — see rules/engine.py and
AdvisoryPanel.tsx on the frontend.
"""
import re

SUPERLATIVE_PATTERNS = [
    re.compile(r"\bbest in (?:india|the world|class)\b", re.IGNORECASE),
    re.compile(r"\b100%\s*(?:pure|natural|safe|guaranteed)\b", re.IGNORECASE),
    re.compile(r"\bno\.?\s*1\s*(?:brand|choice)\b", re.IGNORECASE),
    re.compile(r"\bmiracle\b", re.IGNORECASE),
    re.compile(r"\bclinically proven\b", re.IGNORECASE),
]

EXTRA_QUANTITY_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s?(g|kg|ml|l)\s*(?:extra|free)\b", re.IGNORECASE)


def check_claims(text: str, declared_net_quantity: float | None = None,
                  declared_unit: str | None = None) -> list[dict]:
    """Return a list of {"pattern": str, "detail": str} advisory flags. Never a compliance verdict."""
    flags: list[dict] = []

    for pattern in SUPERLATIVE_PATTERNS:
        match = pattern.search(text)
        if match:
            flags.append({
                "pattern": "unsubstantiated_superlative",
                "detail": f"Unsubstantiated claim detected: \"{match.group(0)}\" — no basis cited in the listing/label text.",
            })

    for match in EXTRA_QUANTITY_PATTERN.finditer(text):
        claimed_qty, claimed_unit = float(match.group(1)), match.group(2).lower()
        if declared_net_quantity is not None and declared_unit and claimed_unit == declared_unit.lower():
            if claimed_qty > declared_net_quantity:
                flags.append({
                    "pattern": "extra_quantity_mismatch",
                    "detail": (
                        f"Listing claims \"{match.group(0)}\" but declared net quantity is only "
                        f"{declared_net_quantity}{declared_unit} — the claimed extra amount exceeds the total declared."
                    ),
                })

    return flags
