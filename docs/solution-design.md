# TruthLabel AI — Solution Design

## 1. Approach

A pipeline that turns a label photo or e-commerce listing into a set of per-field compliance findings, each traceable to a specific LMPC 2011 clause. The pipeline is deliberately split into independent, swappable stages so any one stage (OCR engine, field classifier, rule set) can be replaced without reworking the rest.

## 2. Architecture

```
 Upload (images / listing URL / listing text)
        │
        ▼
 ┌─────────────────┐
 │  Preprocessing   │  deskew, denoise, contrast, panel bbox
 └────────┬─────────┘
          ▼
 ┌─────────────────┐
 │       OCR        │  text regions + bbox + confidence
 └────────┬─────────┘
          ▼
 ┌─────────────────┐
 │ Field Classifier │  region → declaration field (LLM few-shot)
 └────────┬─────────┘
          ▼
 ┌─────────────────┐      ┌───────────────────┐
 │   Rule Engine    │◄─────│ Font / Layout      │
 │ (presence,format)│      │ checks (bbox-based)│
 └────────┬─────────┘      └───────────────────┘
          ▼
 ┌─────────────────┐
 │ Claims Advisory  │  independent tier-3 pass (LLM)
 └────────┬─────────┘
          ▼
 ┌─────────────────┐
 │  Findings store  │  rule_id, clause_ref, verdict, tier
 └────────┬─────────┘
          ▼
 ┌─────────────────┐
 │  Report Builder  │  PDF + editable export
 └─────────────────┘
```

## 3. Key Design Decisions

### 3.1 Separate OCR from field classification
OCR returns raw text regions with bounding boxes; a distinct LLM-based classifier maps regions to declaration fields. This keeps OCR engine choice (PaddleOCR vs EasyOCR vs cloud) independent from the mapping logic, and lets the classifier be swapped for a fine-tuned NER model later without touching OCR.

### 3.2 Declarative, versioned rule engine
Rules live in YAML (`ruleset_v1.yaml`), not code, so each rule's LMPC clause reference is a single, auditable source of truth and rules can be amended without redeploying. Every finding stores which ruleset version evaluated it, so past reports stay reproducible.

### 3.3 Font-size scale reference: user-declared dimension (v1)
Converting pixel height to millimeters needs a scale reference. A reference object in-frame is more robust but unreliable for a user to comply with consistently during a demo. v1 asks the user to declare one package dimension at upload time and derives px-per-mm from it. This is a known simplification, tracked in "Still Open."

### 3.4 Panel placement checked via user-tagged panel type, not auto-detection
True principal-display-panel inference is a hard CV problem. v1 trusts the user's front/back/side tag as a proxy and checks that mandatory declarations fall within the tagged "front" panel's bounding box.

### 3.5 Compliance verdicts and advisory claims are never merged
Tier 1/2 findings (presence, format, font, placement) are rule-based and directly cite LMPC clauses. Tier 3 (misleading marketing claims) is LLM-judgment-based and inherently softer. Keeping them in separate findings/tiers and separate UI sections (`AdvisoryPanel.tsx`) prevents a low-confidence advisory flag from being mistaken for a citable violation.

### 3.6 Confidence-aware "not detected" handling
A declaration below the confidence threshold is never treated as absent (which would silently produce a false non-compliance verdict). It renders as `NOT_DETECTED — needs review`, forcing inspector judgment instead of an automated false positive.

### 3.7 Override without overwrite
Inspector overrides are stored alongside — not instead of — the automated finding, with a mandatory reason. This preserves an audit trail and creates a signal (override rate per rule) useful for tuning the rule set over time.

### 3.8 Async scan processing
Pipeline stages (OCR, classification, rule evaluation, advisory pass, report pre-build) run as a background job; the API returns immediately with `status=processing` and the frontend polls. This avoids blocking on OCR/LLM latency and matches the multi-stage pipeline's natural async shape.

## 4. Data Flow Summary

Scan submission → `scans`/`scan_images` rows created → pipeline populates `declarations` → rule engine + font/layout checks populate `findings` (tiers 1–2) → advisory pass adds tier-3 `findings` → report pre-built → inspector reviews/overrides → export.

## 5. Trade-offs Accepted for v1

- LLM-based field classification over a trained NER model: faster to stand up, no labeled training set required, but higher per-scan latency/cost and less deterministic than a trained model.
- User-declared scale reference over in-frame reference object: simpler UX for a demo, less robust to user error.
- User-tagged panel type over automatic principal-panel detection: avoids a hard CV problem, shifts correctness burden to the user's tagging.

---
*See [PRD.md](PRD.md) for requirements and [fulldesign.md](fulldesign.md) for implementation-level detail. Keep all three in sync when scope changes.*
