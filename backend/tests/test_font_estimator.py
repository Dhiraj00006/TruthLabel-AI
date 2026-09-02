from app.pipeline.font_estimator import measured_height_mm, px_per_mm


def test_px_per_mm():
    assert px_per_mm(declared_dimension_mm=100, declared_dimension_px=1000) == 10


def test_measured_height_mm():
    ratio = px_per_mm(declared_dimension_mm=100, declared_dimension_px=1000)
    assert measured_height_mm(bbox_height_px=15, px_per_mm_ratio=ratio) == 1.5
