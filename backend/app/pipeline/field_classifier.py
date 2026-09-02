"""Maps OCR regions to declaration fields via LLM few-shot classification."""


def classify_regions(ocr_regions: list[dict]) -> list[dict]:
    """Return a list of {"region_index": int, "field_name": str | None, "confidence": float}."""
    raise NotImplementedError
