"""OCR wrapper. Swappable backend (PaddleOCR / EasyOCR / cloud API)."""


def run_ocr(image_path: str) -> list[dict]:
    """Return a list of {"text": str, "bbox": {x,y,w,h}, "confidence": float}."""
    raise NotImplementedError
