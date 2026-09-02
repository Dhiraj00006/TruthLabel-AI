from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.declaration import Declaration
from app.models.finding import Finding
from app.models.scan import Scan
from app.reportgen.pdf_report import render_html

router = APIRouter()


@router.get("/scans/{scan_id}/report.pdf", response_class=HTMLResponse)
def get_report_pdf(scan_id: int, db: Session = Depends(get_db)):
    """Serves the HTML report (see reportgen/pdf_report.py for why this isn't a real PDF yet)."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()
    declarations = db.query(Declaration).filter(Declaration.scan_id == scan_id).all()
    return render_html(scan, findings, declarations)


@router.get("/scans/{scan_id}/report.json")
def get_report_editable(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()
    declarations = db.query(Declaration).filter(Declaration.scan_id == scan_id).all()
    return {
        "scan": {
            "id": scan.id,
            "product_name": scan.product_name,
            "manufacturer_name": scan.manufacturer_name,
            "category": scan.category,
            "status": scan.status,
        },
        "findings": [
            {
                "field_name": f.field_name,
                "verdict": f.verdict,
                "rule_id": f.rule_id,
                "clause_ref": f.rule_clause_ref,
                "detail_message": f.detail_message,
                "tier": f.tier,
                "overridden_by": f.overridden_by,
                "override_reason": f.override_reason,
            }
            for f in findings
        ],
        "declarations": [
            {
                "field_name": d.field_name,
                "raw_text": d.raw_text,
                "normalized_value": d.normalized_value,
                "confidence": d.confidence,
            }
            for d in declarations
        ],
    }
