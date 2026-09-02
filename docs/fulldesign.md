# TruthLabel AI — Full Technical Design

Expands PRD.md and solution-design.md into implementation-level detail: repo structure, module specs, data model, API surface, and detailed workflows.

---

## 1. Repository Structure

```
truthlabel-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint
│   │   ├── api/
│   │   │   ├── scans.py                # upload/scan endpoints
│   │   │   ├── listings.py             # e-commerce listing endpoints
│   │   │   ├── reports.py              # report generation/export endpoints
│   │   │   ├── dashboard.py            # analytics/search endpoints
│   │   │   └── auth.py                 # login, JWT issuance
│   │   ├── pipeline/
│   │   │   ├── preprocess.py           # deskew, denoise, contrast, panel detection
│   │   │   ├── ocr.py                  # OCR wrapper (PaddleOCR/EasyOCR)
│   │   │   ├── field_classifier.py     # tags OCR regions -> declaration fields
│   │   │   ├── font_estimator.py       # pixel height -> mm, scale reference logic
│   │   │   ├── layout_checker.py       # principal display panel grouping check
│   │   │   ├── listing_parser.py       # scrape/parse e-commerce listing text
│   │   │   └── claims_advisory.py      # tier-3 misleading-claims flagging (LLM)
│   │   ├── rules/
│   │   │   ├── engine.py               # loads rule config, evaluates fields
│   │   │   └── ruleset_v1.yaml         # versioned declarative rules (Third Schedule)
│   │   ├── models/                     # SQLAlchemy models
│   │   │   ├── scan.py
│   │   │   ├── declaration.py
│   │   │   ├── finding.py
│   │   │   ├── user.py
│   │   │   └── report.py
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── reportgen/
│   │   │   ├── pdf_report.py           # WeasyPrint/ReportLab report builder
│   │   │   └── templates/
│   │   ├── db.py
│   │   └── config.py
│   ├── tests/
│   │   ├── fixtures/                   # sample + synthetically-violated label images
│   │   ├── test_ocr.py
│   │   ├── test_rules.py
│   │   └── test_font_estimator.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── upload.tsx              # image/listing submission flow
│   │   │   ├── scan-result.tsx         # per-field compliance breakdown view
│   │   │   ├── dashboard.tsx           # analytics + trends
│   │   │   ├── history.tsx             # scan repository, search/filter
│   │   │   └── login.tsx
│   │   ├── components/
│   │   │   ├── FieldFindingCard.tsx
│   │   │   ├── EvidenceViewer.tsx
│   │   │   ├── ConfidenceBadge.tsx
│   │   │   └── AdvisoryPanel.tsx        # visually separated tier-3 findings
│   │   └── lib/api.ts
│   └── package.json
├── data/
│   ├── sample_labels/                  # sourced real product images
│   └── synthetic_violations/           # deliberately-edited non-compliant variants
├── docs/
│   └── (mirrors project docs: PRD.md, solution-design.md, fulldesign.md)
└── docker-compose.yml                  # postgres + backend + frontend for local/demo
```

---

## 2. Data Model (Postgres)

**users**
`id, name, email, password_hash, role (inspector|admin), created_at`

**scans**
`id, submitted_by (user_id), source_type (image|listing), product_name, manufacturer_name, category, net_quantity_declared, net_quantity_unit, status (processing|complete|failed), created_at`

**scan_images**
`id, scan_id, panel_type (front|back|side|unknown), image_url, width_px, height_px`

**declarations** (one row per extracted field instance)
`id, scan_id, field_name (enum: mfr_address, net_quantity, mrp, mfg_date, consumer_care, country_of_origin, unit_sale_price, commodity_name), raw_text, normalized_value, bounding_box (json: x,y,w,h,image_id), confidence (float)`

**findings** (one row per rule evaluated against a declaration)
`id, scan_id, declaration_id (nullable — null if field NOT_DETECTED), rule_id, rule_clause_ref, verdict (compliant|non_compliant|not_detected), detail_message, tier (1_presence|2_format_placement|3_advisory), overridden_by (user_id, nullable), override_reason (nullable)`

**reports**
`id, scan_id, pdf_url, editable_url, generated_at`

**listings**
`id, scan_id, source_url, raw_text, scraped_at`

Indexes: `scans(manufacturer_name, category, created_at)` for dashboard trend queries; `findings(verdict, tier)` for violation analytics.

---

## 3. Module-by-Module Functional Detail

### 3.1 Preprocessing (`preprocess.py`)
- Deskew via contour/Hough-line detection
- Denoise (bilateral filter), contrast normalization (CLAHE)
- Panel detection: heuristic (largest rectangular contour per uploaded image = one panel) — v1 assumes one panel per uploaded image, multi-panel-per-photo detection is a stretch
- Output: cleaned image + detected panel bounding box

### 3.2 OCR (`ocr.py`)
- Wraps PaddleOCR (primary candidate — strong multi-language incl. Hindi support) with a swappable interface so EasyOCR/cloud API can be A/B tested
- Returns list of `{text, bbox, confidence}` per detected text region — never a single flattened string, since bbox is required for font-size and layout checks downstream

### 3.3 Field Classifier (`field_classifier.py`)
- Input: list of OCR regions for a scan
- v1 approach: LLM few-shot prompt — given all OCR text+positions for a panel, return a structured mapping of `region_index -> field_name (or null)`, with a confidence score
- Stretch: replace/augment with a fine-tuned NER model if time allows and a labeled set exists
- Must handle: fields split across multiple OCR regions (e.g. address wrapping two lines), and fields with no match (returns NOT_DETECTED downstream)

### 3.4 Font Estimator (`font_estimator.py`)
- Requires a scale reference to convert pixel height → mm. **Decision for v1: user-declared package dimension at upload time** (e.g. "this package is 10cm tall"), used to compute px-per-mm for that image. (Reference-object-in-frame deferred — harder for users to comply with reliably in a demo.)
- For each classified declaration's bounding box: measured_height_mm = bbox_height_px / px_per_mm
- Compared against `min_font_mm_by_net_qty` table in the rule engine for that scan's declared net quantity slab

### 3.5 Layout Checker (`layout_checker.py`)
- Checks that all mandatory declarations' bounding boxes fall within one detected panel region (principal display panel proxy = the panel the user marked/uploaded as "front")
- v1 simplification: relies on user-tagged panel type rather than automatic principal-panel inference

### 3.6 Rule Engine (`rules/engine.py` + `ruleset_v1.yaml`)
- Loads YAML ruleset at startup (hot-reloadable for demo purposes)
- For each declaration field, evaluates: presence rule → format rule (regex/whitelist) → font-size rule (if applicable) → placement rule
- Each rule carries a `clause_ref` string (e.g. `"LMPC 2011, Rule 6(1)(e), Third Schedule"`) that gets attached to every finding for traceability (NFR2)
- Example ruleset entry:
```yaml
- field: mrp
  clause_ref: "LMPC 2011, Rule 6(1)(f)"
  required: true
  format_regex: "MRP.*(Rs\\.?|₹)\\s?\\d+(\\.\\d{2})?.*incl.*tax"
  format_error: "MRP must be stated inclusive of all taxes"
- field: net_quantity
  clause_ref: "LMPC 2011, Rule 6(1)(c), Second Schedule"
  required: true
  unit_whitelist: [g, kg, ml, l, N, "cm", "m"]
- field: mfg_date
  clause_ref: "LMPC 2011, Rule 6(1)(d)"
  required: true
  format_regex: "\\b(0[1-9]|1[0-2])[\\/\\-\\s](19|20)\\d{2}\\b"
font_rules:
  min_font_mm_by_net_qty:
    "<=200_g_ml": 1.0
    "200-500_g_ml": 1.5
    ">500_g_ml": 2.0
```

### 3.7 Listing Parser (`listing_parser.py`)
- Given a URL: fetch + parse product title/bullets/description (platform-specific selectors as a stretch; generic text-block extraction for v1)
- Given pasted text: pass directly to field classifier
- Any listing images get routed through the image pipeline (3.1–3.5)

### 3.8 Advisory Claims Module (`claims_advisory.py`, tier 3)
- LLM-based check against a small curated pattern set: unsubstantiated superlatives ("best in India"), quantity-claim mismatches (declared net qty vs. marketing text like "500g free" not matching), missing basis for "extra %" claims
- Output tagged `tier: 3_advisory` and **never merged into the compliant/non-compliant field verdicts** — rendered in a visually distinct "Advisory" section of the report and UI (`AdvisoryPanel.tsx`)

### 3.9 Report Generator (`reportgen/pdf_report.py`)
- Template-driven (Jinja2 → WeasyPrint or ReportLab): header (product/manufacturer/scan metadata) → per-field findings table with clause references → evidence photos with bbox overlays → advisory section → inspector override log
- Exports both PDF and an editable format (e.g. DOCX or structured JSON for re-import)

### 3.10 Dashboard/Analytics (`dashboard.py`)
- Aggregate queries: violation count by category/manufacturer/time range, most-common violated field, override rate (findings inspectors disagreed with — useful signal for rule-tuning)
- Search/filter over `scans` + `findings`

---

## 4. API Surface (v1)

```
POST   /auth/login
POST   /scans                 -> create scan, upload images, returns scan_id (async processing)
GET    /scans/{id}             -> scan status + full findings breakdown
POST   /scans/{id}/override    -> inspector overrides a finding
POST   /listings               -> submit URL or text, returns scan_id
GET    /scans/{id}/report.pdf
GET    /scans/{id}/report.docx (or .json editable)
GET    /dashboard/summary?category=&manufacturer=&from=&to=
GET    /scans?search=&category=&manufacturer=&status=
```

Processing is async: `POST /scans` returns immediately with `status=processing`; frontend polls or uses a websocket/SSE for completion (v1: polling is sufficient).

---

## 5. Detailed Workflow — Image Path (sequence)

1. Inspector uploads 1–3 images, tags each as front/back/side, enters declared net quantity + unit and package height (for font scale reference)
2. Backend creates `scan` + `scan_images` rows, kicks off async pipeline
3. Preprocess → OCR → Field Classifier populates `declarations`
4. Rule Engine evaluates each declaration + checks for missing required fields → populates `findings` (tiers 1 & 2)
5. Font Estimator + Layout Checker contribute additional findings using the same `findings` table
6. Claims Advisory module runs independently, tier 3 findings
7. `scan.status = complete`; report generator pre-builds PDF
8. Inspector views `scan-result.tsx`: per-field cards (compliant/non-compliant/needs-review + clause ref + confidence), advisory panel separated below, can override any finding with a reason
9. Inspector downloads/exports report

## 6. Detailed Workflow — Listing Path

1. Inspector submits URL or pastes listing text
2. Listing Parser extracts text blocks (+ any images, routed through image path)
3. Same Field Classifier → Rule Engine flow as above, minus font-size/layout checks (not applicable to text-only listings unless images present)
4. Report generated the same way, noting `source_type = listing`

---

## 7. Non-Functional Detailing

- **Auditability (NFR2):** every finding row stores its `rule_id` and `clause_ref` — the report can never show a violation without citing what was violated
- **Confidence surfacing (NFR3):** any declaration with classifier confidence below a configurable threshold is rendered as `NOT_DETECTED — needs review`, never silently treated as absent-and-therefore-violating
- **Rule versioning (NFR1):** `ruleset_v1.yaml` is loaded by version; findings store which ruleset version produced them, so historical reports remain reproducible even if rules are later amended
- **Override logging (traceability):** any inspector override is stored with user + reason, never silently replaces the automated finding (both are kept)

## 8. Deployment (demo-scope)

- `docker-compose.yml`: postgres + backend (FastAPI/uvicorn) + frontend (Next.js) — single command spin-up for judges/demo
- Environment config via `.env` (DB url, OCR engine choice, LLM API key)
- No production hardening (rate limiting, full auth flows) required for hackathon demo, but noted as future work

## 9. Still Open (carried from PRD/solution-design)

- Font-size scale reference: confirmed for v1 as user-declared package dimension (see 3.4) — revisit if reference-object approach becomes feasible
- OCR engine benchmark not yet run
- Panel detection is heuristic/user-tagged in v1 — automatic principal-display-panel inference is future work
- Team role split / day-by-day schedule still not defined

---
*Builds on: PRD.md (requirements), solution-design.md (architecture rationale). Keep all three in sync when scope changes.*
