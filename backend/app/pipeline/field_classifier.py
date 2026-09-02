"""Maps raw text (from a listing) or OCR regions (from a label image) to declaration fields.

v1 status:
- Text path (`classify_text`): real regex/keyword heuristics — no LLM required yet.
- Image path (`classify_regions`): OCR is not wired up yet, so this returns no matches;
  every field surfaces as NOT_DETECTED — needs review (see rules/engine.py), never as a
  silent violation.
"""
import re

FIELD_PATTERNS: dict[str, re.Pattern] = {
    "mrp": re.compile(r"(?:MRP|M\.R\.P\.?)[^\n\d]{0,20}(Rs\.?|₹)\s?\d+(?:\.\d{2})?[^\n]{0,40}", re.IGNORECASE),
    "net_quantity": re.compile(r"\bNet\s*(?:Qty|Quantity|Wt|Weight)?\.?[:\s]{0,5}\d+(?:\.\d+)?\s?(kg|g|ml|l|N|cm|m)\b", re.IGNORECASE),
    "mfg_date": re.compile(r"\b(?:Mfg|Manufactured|Packed|Pkd)\.?\s*(?:Date|On)?[:\s]{0,5}(0[1-9]|1[0-2])[\/\-\s](19|20)\d{2}\b", re.IGNORECASE),
    "consumer_care": re.compile(r"(?:Consumer\s*Care|Customer\s*Care)[^\n]{0,100}", re.IGNORECASE),
    "country_of_origin": re.compile(r"(?:Country\s*of\s*Origin|Made\s*in)[:\s]{0,5}([A-Za-z\s]{2,30})", re.IGNORECASE),
    "unit_sale_price": re.compile(r"(?:Unit\s*Sale\s*Price|Price\s*per\s*(?:kg|g|ml|l))[^\n]{0,60}", re.IGNORECASE),
    "mfr_address": re.compile(r"(?:Marketed\s*by|Mfd\.?\s*by|Manufactured\s*by)[:\s]*[^\n]{5,150}", re.IGNORECASE),
}

HIGH_CONFIDENCE = 0.9


def classify_text(text: str, fallback_commodity_name: str | None = None) -> dict[str, dict]:
    """Return {field_name: {"raw_text": str, "normalized_value": str, "confidence": float}}."""
    results: dict[str, dict] = {}
    for field_name, pattern in FIELD_PATTERNS.items():
        match = pattern.search(text)
        if match:
            raw = match.group(0).strip()
            results[field_name] = {
                "raw_text": raw,
                "normalized_value": raw,
                "confidence": HIGH_CONFIDENCE,
            }
    if "commodity_name" not in results and fallback_commodity_name:
        results["commodity_name"] = {
            "raw_text": fallback_commodity_name,
            "normalized_value": fallback_commodity_name,
            "confidence": HIGH_CONFIDENCE,
        }
    return results


def classify_regions(ocr_regions: list[dict]) -> dict[str, dict]:
    """OCR is not wired up in v1 — always returns no matches (fields render as NOT_DETECTED)."""
    return {}
