from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
def dashboard_summary(category: str | None = None, manufacturer: str | None = None,
                       from_: str | None = None, to: str | None = None):
    """Aggregate violation counts by category/manufacturer/time range."""
    raise NotImplementedError
