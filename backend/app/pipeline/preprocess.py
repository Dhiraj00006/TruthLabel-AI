"""Deskew, denoise, contrast-normalize an uploaded label image and detect its panel bbox."""


def preprocess_image(image_path: str) -> dict:
    """Return {"cleaned_image_path": str, "panel_bbox": {x, y, w, h}}."""
    raise NotImplementedError
