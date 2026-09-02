from fastapi import FastAPI

from app.api import auth, dashboard, listings, reports, scans

app = FastAPI(title="TruthLabel AI")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(scans.router, prefix="/scans", tags=["scans"])
app.include_router(listings.router, prefix="/listings", tags=["listings"])
app.include_router(reports.router, tags=["reports"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])


@app.get("/health")
def health():
    return {"status": "ok"}
