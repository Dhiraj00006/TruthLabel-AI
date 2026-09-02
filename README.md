# TruthLabel AI

AI-assisted compliance checking for packaged-commodity labels and e-commerce
listings against India's Legal Metrology (Packaged Commodities) Rules, 2011.

## Docs

- [docs/PRD.md](docs/PRD.md) — requirements
- [docs/solution-design.md](docs/solution-design.md) — architecture rationale
- [docs/fulldesign.md](docs/fulldesign.md) — implementation-level detail

## Quickstart (demo)

```
docker-compose up
```

Backend: http://localhost:8000 (docs at `/docs`)
Frontend: http://localhost:3000

## Repo layout

- `backend/` — FastAPI service: OCR/classification pipeline, rule engine, report generation
- `frontend/` — Next.js inspector UI
- `data/` — sample and synthetically-violated label images for testing
