from fastapi import APIRouter

router = APIRouter()


@router.post("")
def create_scan():
    """Create a scan from uploaded images, kick off async pipeline, return scan_id."""
    raise NotImplementedError


@router.get("/{scan_id}")
def get_scan(scan_id: int):
    """Return scan status and full findings breakdown."""
    raise NotImplementedError


@router.post("/{scan_id}/override")
def override_finding(scan_id: int):
    """Record an inspector override for a finding, with reason."""
    raise NotImplementedError


@router.get("")
def list_scans(search: str | None = None, category: str | None = None,
               manufacturer: str | None = None, status: str | None = None):
    """Search/filter scan history."""
    raise NotImplementedError
