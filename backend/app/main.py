from fastapi import FastAPI

from app.api import auth, dashboard, listings, reports, scans
from app.auth import hash_password
from app.db import Base, SessionLocal, engine
from app.models.user import User, UserRole

app = FastAPI(title="TruthLabel AI")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(scans.router, prefix="/scans", tags=["scans"])
app.include_router(listings.router, prefix="/listings", tags=["listings"])
app.include_router(reports.router, tags=["reports"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])


@app.on_event("startup")
def on_startup():
    import app.models  # noqa: F401 register all models with Base before create_all

    Base.metadata.create_all(bind=engine)
    _seed_demo_user()


def _seed_demo_user():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(
                name="Demo Inspector",
                email="inspector@truthlabel.ai",
                password_hash=hash_password("demo1234"),
                role=UserRole.inspector,
            ))
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
