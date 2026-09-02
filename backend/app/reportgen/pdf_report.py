"""Builds the per-scan PDF (and editable) report from findings + evidence images."""


def generate_pdf_report(scan_id: int) -> str:
    """Render templates/report.html with scan data and return the output PDF path."""
    raise NotImplementedError


def generate_editable_report(scan_id: int) -> str:
    """Return a DOCX or structured JSON path for re-import/editing."""
    raise NotImplementedError
