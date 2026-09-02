# TruthLabel AI — Product Requirements Document

## 1. Problem

Packaged-commodity labels in India must comply with the Legal Metrology (Packaged Commodities) Rules, 2011 (LMPC 2011) — mandatory declarations like MRP, net quantity, manufacturer address, mfg date, consumer care details, country of origin, unit sale price, and commodity name, each with format, font-size, and placement requirements. Manual inspection of physical labels and e-commerce listings for compliance is slow, inconsistent, and hard to audit. Inspectors need a tool that flags non-compliant declarations with a clear citation to the violated rule, works from photos or e-commerce listing text/URLs, and produces an exportable, auditable report.

## 2. Goals

- Detect presence, format, font-size, and placement violations of mandatory LMPC declarations from label photos.
- Support e-commerce listing text/URL as an alternate input path.
- Surface a confidence-tagged breakdown per field — never silently treat "not detected" as "violating."
- Cite the specific LMPC rule/schedule clause for every finding (auditability).
- Flag advisory-only issues (misleading marketing claims) in a visually separate tier, never mixed into compliance verdicts.
- Let inspectors override any automated finding, with the override and its reason permanently logged.
- Provide a dashboard for trend/violation analytics across manufacturers/categories/time.
- Export a report (PDF + editable format) per scan.

## 3. Non-Goals (v1)

- Automatic principal-display-panel inference (v1 relies on user-tagged panel type).
- Reference-object-based font scale calibration (v1 uses user-declared package dimension instead).
- Production-grade auth hardening, rate limiting (hackathon/demo scope only).
- Multi-panel detection within a single uploaded photo.

## 4. Users

- **Inspector**: uploads/scans labels or listings, reviews findings, overrides, exports reports.
- **Admin**: same as inspector, plus (future) rule configuration and dashboard-wide visibility.

## 5. Functional Requirements

- FR1: Accept 1–3 label images per scan, tagged front/back/side, with declared net quantity + unit and package height.
- FR2: Accept an e-commerce listing via URL or pasted text as an alternate scan source.
- FR3: Run OCR + field classification to extract each mandatory declaration with a bounding box and confidence score.
- FR4: Evaluate each declaration against a versioned rule set (presence → format → font-size → placement) and record a per-field finding with clause reference.
- FR5: Run an independent advisory pass for misleading-claims patterns, tagged tier 3 and never merged into compliance verdicts.
- FR6: Let an inspector override any finding with a mandatory reason; store both the original and the override.
- FR7: Generate a PDF and an editable (DOCX/JSON) report per scan, including evidence images with bounding-box overlays.
- FR8: Provide a searchable/filterable scan history and a dashboard of aggregate violation trends.

## 6. Non-Functional Requirements

- NFR1 (Rule versioning): findings must record which ruleset version produced them; historical reports stay reproducible after rules are amended.
- NFR2 (Auditability): every finding must carry a `rule_id` and `clause_ref`; no violation may be shown without citing the rule violated.
- NFR3 (Confidence surfacing): low-confidence extractions render as `NOT_DETECTED — needs review`, never as an assumed violation.
- NFR4 (Traceability): overrides are logged with user + reason and never replace the automated finding.

## 7. Success Metrics (demo scope)

- Correctly classifies and evaluates the 8 mandatory fields on a representative sample of real + synthetically-violated label images.
- Every finding shown in the UI/report traces to a specific LMPC clause.
- End-to-end scan (upload → findings → report) completes without manual intervention for the happy path.

---
*See [solution-design.md](solution-design.md) for architecture rationale and [fulldesign.md](fulldesign.md) for implementation-level detail. Keep all three in sync when scope changes.*
