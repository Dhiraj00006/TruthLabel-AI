"""Tier-3 LLM-based check for unsubstantiated marketing claims. Output never merged into
compliance verdicts (tiers 1-2); always rendered as a separate advisory section."""


def check_claims(listing_or_label_text: str, declared_net_quantity: float | None = None) -> list[dict]:
    """Return a list of {"pattern": str, "detail": str, "tier": "3_advisory"}."""
    raise NotImplementedError
