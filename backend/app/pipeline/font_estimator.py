"""Converts bounding-box pixel height to mm using a user-declared package dimension as scale reference."""


def px_per_mm(declared_dimension_mm: float, declared_dimension_px: float) -> float:
    return declared_dimension_px / declared_dimension_mm


def measured_height_mm(bbox_height_px: float, px_per_mm_ratio: float) -> float:
    return bbox_height_px / px_per_mm_ratio
