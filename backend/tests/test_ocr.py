import pytest

from app.pipeline.ocr import run_ocr


def test_run_ocr_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        run_ocr("app/tests/fixtures/does_not_exist.jpg")
