from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models.finding import Finding
from app.models.scan import Scan, ScanStatus, SourceType
from app.schemas.scan import OverrideRequest, ScanResponse, ScanSummary
from app.services.scan_processor import process_image_scan

router = APIRouter()


@router.post("", response_model=ScanResponse)
def create_scan(
    product_name: str | None = None,
    manufacturer_name: str | None = None,
    category: str | None = None,
    net_quantity_declared: float | None = None,
    net_quantity_unit: str | None = None,
    submitted_by: int = 1,
    db: Session = Depends(get_db),
):
    """Create an image-sourced scan. Image upload/OCR is not wired up yet (see
    pipeline/ocr.py) — the scan is created and evaluated immediately, with every
    mandatory field surfacing as NOT_DETECTED pending manual review."""
    scan = Scan(
        submitted_by=submitted_by,
        source_type=SourceType.image,
        product_name=product_name,
        manufacturer_name=manufacturer_name,
        category=category,
        net_quantity_declared=net_quantity_declared,
        net_quantity_unit=net_quantity_unit,
        status=ScanStatus.processing,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    process_image_scan(db, scan)
    return scan


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).options(
        selectinload(Scan.findings), selectinload(Scan.declarations)
    ).filter(Scan.id == scan_id).first()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.post("/{scan_id}/override", response_model=ScanResponse)
def override_finding(scan_id: int, payload: OverrideRequest, overridden_by: int = 1, db: Session = Depends(get_db)):
    """Record an inspector override. The automated finding is kept, not replaced —
    only overridden_by/override_reason are set alongside it (traceability, NFR4)."""
    finding = db.query(Finding).filter(Finding.id == payload.finding_id, Finding.scan_id == scan_id).first()
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found for this scan")

    finding.overridden_by = overridden_by
    finding.override_reason = payload.reason
    db.commit()

    scan = db.query(Scan).options(
        selectinload(Scan.findings), selectinload(Scan.declarations)
    ).filter(Scan.id == scan_id).first()
    return scan


@router.get("", response_model=list[ScanSummary])
def list_scans(
    search: str | None = None,
    category: str | None = None,
    manufacturer: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Scan)
    if search:
        like = f"%{search}%"
        query = query.filter(Scan.product_name.ilike(like) | Scan.manufacturer_name.ilike(like))
    if category:
        query = query.filter(Scan.category == category)
    if manufacturer:
        query = query.filter(Scan.manufacturer_name == manufacturer)
    if status:
        query = query.filter(Scan.status == status)
    return query.order_by(Scan.created_at.desc()).all()
