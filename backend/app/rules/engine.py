"""Loads the declarative ruleset and evaluates extracted declarations against it.

Every finding produced here carries the rule's clause_ref (NFR2 auditability) and the
ruleset version that produced it (NFR1 reproducibility). A field with no extraction, or
one below the confidence threshold, always yields verdict "not_detected" — never
"non_compliant" — so a missed extraction can never masquerade as a violation (NFR3).
"""
import re

import yaml

from app.config import settings

CONFIDENCE_THRESHOLD = 0.6


def load_ruleset(path: str | None = None) -> dict:
    with open(path or settings.ruleset_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def evaluate_declarations(
    declarations: dict[str, dict],
    ruleset: dict,
    net_quantity_unit: str | None = None,
) -> list[dict]:
    """declarations: {field_name: {"raw_text", "normalized_value", "confidence"} or absent}.

    Returns a list of finding dicts: field_name, rule_id, clause_ref, verdict,
    detail_message, tier, ruleset_version.
    """
    version = ruleset.get("version", 1)
    findings: list[dict] = []

    for field_def in ruleset["fields"]:
        field_name = field_def["field"]
        clause_ref = field_def["clause_ref"]
        required = field_def.get("required", False)
        declaration = declarations.get(field_name)

        rule_id = f"{field_name}.presence"

        if declaration is None or declaration.get("confidence", 0) < CONFIDENCE_THRESHOLD:
            if required:
                findings.append({
                    "field_name": field_name,
                    "rule_id": rule_id,
                    "clause_ref": clause_ref,
                    "verdict": "not_detected",
                    "detail_message": f"{field_name} was not detected with sufficient confidence — needs manual review.",
                    "tier": "1_presence",
                    "ruleset_version": version,
                })
            continue

        raw_text = declaration.get("normalized_value", "")

        format_regex = field_def.get("format_regex")
        if format_regex and not re.search(format_regex, raw_text, re.IGNORECASE):
            findings.append({
                "field_name": field_name,
                "rule_id": f"{field_name}.format",
                "clause_ref": clause_ref,
                "verdict": "non_compliant",
                "detail_message": field_def.get("format_error", f"{field_name} does not match the required format."),
                "tier": "2_format_placement",
                "ruleset_version": version,
            })
            continue

        unit_whitelist = field_def.get("unit_whitelist")
        if unit_whitelist and net_quantity_unit and net_quantity_unit not in unit_whitelist:
            findings.append({
                "field_name": field_name,
                "rule_id": f"{field_name}.unit",
                "clause_ref": clause_ref,
                "verdict": "non_compliant",
                "detail_message": f"Unit '{net_quantity_unit}' is not among the permitted units: {', '.join(unit_whitelist)}.",
                "tier": "2_format_placement",
                "ruleset_version": version,
            })
            continue

        findings.append({
            "field_name": field_name,
            "rule_id": rule_id,
            "clause_ref": clause_ref,
            "verdict": "compliant",
            "detail_message": f"{field_name} present and matches required format.",
            "tier": "1_presence",
            "ruleset_version": version,
        })

    return findings


def evaluate_font_sizes(
    font_measurements: dict[str, float],
    ruleset: dict,
    net_quantity_declared: float,
    net_quantity_unit: str,
) -> list[dict]:
    """font_measurements: {field_name: measured_height_mm}. Only meaningful for image scans
    where a scale reference (user-declared package dimension) was supplied."""
    version = ruleset.get("version", 1)
    min_by_slab = ruleset.get("font_rules", {}).get("min_font_mm_by_net_qty", {})

    if net_quantity_unit in ("g", "ml"):
        if net_quantity_declared <= 200:
            slab = "<=200_g_ml"
        elif net_quantity_declared <= 500:
            slab = "200-500_g_ml"
        else:
            slab = ">500_g_ml"
    else:
        slab = None

    min_mm = min_by_slab.get(slab) if slab else None
    if min_mm is None:
        return []

    findings = []
    for field_name, height_mm in font_measurements.items():
        compliant = height_mm >= min_mm
        findings.append({
            "field_name": field_name,
            "rule_id": f"{field_name}.font_size",
            "clause_ref": "LMPC 2011, Rule 6(3), Third Schedule",
            "verdict": "compliant" if compliant else "non_compliant",
            "detail_message": (
                f"Measured font height {height_mm:.2f}mm "
                f"{'meets' if compliant else 'is below'} the required minimum {min_mm}mm for this net quantity slab."
            ),
            "tier": "2_format_placement",
            "ruleset_version": version,
        })
    return findings
