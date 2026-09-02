from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
def login():
    """Issue a JWT for a valid inspector/admin credential pair."""
    raise NotImplementedError
