"""Orchestrates the pipeline for a single scan: classify -> rule-evaluate -> advisory-check
-> persist declarations/findings -> mark the scan complete.

Runs synchronously in-process for now (the stub classifier/advisory checks are fast).
Swap this for a real background task queue once OCR/LLM calls are wired in (they will
be slow enough that request-blocking processing is no longer acceptable).
"""
from sqlalchemy.orm import Session

from app.models.declaration import Declaration
from app.models.finding import Finding
from app.models.scan import Scan, ScanStatus
from app.pipeline.claims_advisory import check_claims
from app.pipeline.field_classifier import classify_regions, classify_text
from app.rules.engine import evaluate_declarations, load_ruleset


def process_text_scan(db: Session, scan: Scan, text: str) -> Scan:
    ruleset = load_ruleset()

    extracted = classify_text(text, fallback_commodity_name=scan.product_name)
    declarations = _persist_declarations(db, scan.id, extracted)

    findings_data = evaluate_declarations(
        {name: extracted[name] for name in extracted},
        ruleset,
        net_quantity_unit=scan.net_quantity_unit,
    )
    _persist_findings(db, scan.id, findings_data, declarations)

    advisory_flags = check_claims(
        text,
        declared_net_quantity=scan.net_quantity_declared,
        declared_unit=scan.net_quantity_unit,
    )
    _persist_advisory_findings(db, scan.id, advisory_flags, ruleset.get("version", 1))

    scan.status = ScanStatus.complete
    db.commit()
    db.refresh(scan)
    return scan


def process_image_scan(db: Session, scan: Scan) -> Scan:
    """OCR is not wired up yet — every mandatory field surfaces as NOT_DETECTED so an
    inspector can review it manually, rather than being silently skipped or marked a
    violation (NFR3)."""
    ruleset = load_ruleset()

    extracted = classify_regions(ocr_regions=[])
    declarations = _persist_declarations(db, scan.id, extracted)

    findings_data = evaluate_declarations(extracted, ruleset, net_quantity_unit=scan.net_quantity_unit)
    _persist_findings(db, scan.id, findings_data, declarations)

    scan.status = ScanStatus.complete
    db.commit()
    db.refresh(scan)
    return scan


def _persist_declarations(db: Session, scan_id: int, extracted: dict[str, dict]) -> dict[str, Declaration]:
    declarations: dict[str, Declaration] = {}
    for field_name, data in extracted.items():
        declaration = Declaration(
            scan_id=scan_id,
            field_name=field_name,
            raw_text=data.get("raw_text"),
            normalized_value=data.get("normalized_value"),
            confidence=data.get("confidence"),
        )
        db.add(declaration)
        db.flush()
        declarations[field_name] = declaration
    return declarations


def _persist_findings(db: Session, scan_id: int, findings_data: list[dict], declarations: dict[str, Declaration]) -> None:
    for f in findings_data:
        declaration = declarations.get(f["field_name"])
        db.add(Finding(
            scan_id=scan_id,
            declaration_id=declaration.id if declaration else None,
            field_name=f["field_name"],
            rule_id=f["rule_id"],
            rule_clause_ref=f["clause_ref"],
            verdict=f["verdict"],
            detail_message=f["detail_message"],
            tier=f["tier"],
            ruleset_version=f["ruleset_version"],
        ))


def _persist_advisory_findings(db: Session, scan_id: int, advisory_flags: list[dict], ruleset_version: int) -> None:
    for flag in advisory_flags:
        db.add(Finding(
            scan_id=scan_id,
            declaration_id=None,
            field_name=None,
            rule_id=f"advisory.{flag['pattern']}",
            rule_clause_ref="Advisory — not an LMPC clause citation",
            verdict="non_compliant",
            detail_message=flag["detail"],
            tier="3_advisory",
            ruleset_version=ruleset_version,
        ))
