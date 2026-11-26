import httpx
from fastapi import HTTPException

from model import TravelRequestModel


def validate_trip(req: TravelRequestModel) -> None:
    """Shared date validation for the /plan and /stream/plan endpoints."""
    if req.start_date > req.end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    trip_days = (req.end_date - req.start_date).days
    if trip_days < 1:
        raise HTTPException(status_code=400, detail="Travel plan must be at least 1 day long")
    if trip_days > 14:
        raise HTTPException(status_code=400, detail="Travel plan cannot be longer than 14 days")


def describe_error(exc: Exception) -> str:
    """Turn an upstream failure into a short, user-readable message."""
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            body = exc.response.json()
            msg = body.get("error", {}).get("message") or body.get("error-type")
        except Exception:
            msg = None
        return f"Upstream service returned {exc.response.status_code}" + (f": {msg}" if msg else "")
    if isinstance(exc, httpx.RequestError):
        return "Could not reach the upstream service. Check your internet connection."
    return str(exc) or exc.__class__.__name__
