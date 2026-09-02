from fastapi import APIRouter

router = APIRouter()


@router.post("")
def create_listing_scan():
    """Submit a listing URL or pasted text, returns scan_id."""
    raise NotImplementedError
