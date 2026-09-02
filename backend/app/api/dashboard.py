from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.finding import Finding
from app.models.scan import Scan

router = APIRouter()


@router.get("/summary")
def dashboard_summary(
    category: str | None = None,
    manufacturer: str | None = None,
    from_: str | None = None,
    to: str | None = None,
    db: Session = Depends(get_db),
):
    scan_query = db.query(Scan)
    if category:
        scan_query = scan_query.filter(Scan.category == category)
    if manufacturer:
        scan_query = scan_query.filter(Scan.manufacturer_name == manufacturer)
    if from_:
        scan_query = scan_query.filter(Scan.created_at >= from_)
    if to:
        scan_query = scan_query.filter(Scan.created_at <= to)

    scan_ids = [s.id for s in scan_query.all()]
    finding_query = db.query(Finding).filter(Finding.scan_id.in_(scan_ids)) if scan_ids else db.query(Finding).filter(False)

    total_scans = len(scan_ids)

    violations_by_field = dict(
        finding_query.filter(Finding.verdict == "non_compliant")
        .with_entities(Finding.field_name, func.count(Finding.id))
        .group_by(Finding.field_name)
        .all()
    )

    violations_by_category = dict(
        scan_query.join(Finding, Finding.scan_id == Scan.id)
        .filter(Finding.verdict == "non_compliant")
        .with_entities(Scan.category, func.count(Finding.id))
        .group_by(Scan.category)
        .all()
    )

    total_findings = finding_query.count()
    overridden_findings = finding_query.filter(Finding.overridden_by.isnot(None)).count()
    override_rate = (overridden_findings / total_findings) if total_findings else 0.0

    return {
        "total_scans": total_scans,
        "violations_by_field": violations_by_field,
        "violations_by_category": violations_by_category,
        "override_rate": override_rate,
    }
