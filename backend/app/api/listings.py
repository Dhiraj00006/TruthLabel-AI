from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models.listing import Listing
from app.models.scan import Scan, ScanStatus, SourceType
from app.pipeline.listing_parser import parse_listing_text, parse_listing_url
from app.schemas.scan import ListingCreateRequest, ScanResponse
from app.services.scan_processor import process_text_scan

router = APIRouter()


@router.post("", response_model=ScanResponse)
def create_listing_scan(payload: ListingCreateRequest, submitted_by: int = 1, db: Session = Depends(get_db)):
    if not payload.source_url and not payload.text:
        raise HTTPException(status_code=400, detail="Provide either source_url or text")

    text = parse_listing_url(payload.source_url) if payload.source_url else parse_listing_text(payload.text)

    scan = Scan(
        submitted_by=submitted_by,
        source_type=SourceType.listing,
        product_name=payload.product_name,
        manufacturer_name=payload.manufacturer_name,
        category=payload.category,
        net_quantity_declared=payload.net_quantity_declared,
        net_quantity_unit=payload.net_quantity_unit,
        status=ScanStatus.processing,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    db.add(Listing(scan_id=scan.id, source_url=payload.source_url, raw_text=text))
    db.commit()

    process_text_scan(db, scan, text)

    scan = db.query(Scan).options(
        selectinload(Scan.findings), selectinload(Scan.declarations)
    ).filter(Scan.id == scan.id).first()
    return scan
