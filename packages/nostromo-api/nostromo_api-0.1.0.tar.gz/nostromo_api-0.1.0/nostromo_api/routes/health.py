"""
Health check route.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from nostromo_core.theme import DISPLAY_NAME, SYSTEM_NAME

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    system: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns system status for monitoring.
    """
    return HealthResponse(
        status="OPERATIONAL",
        system=SYSTEM_NAME,
        message=f"{DISPLAY_NAME} SYSTEMS NOMINAL.",
    )


@router.get("/")
async def root() -> dict:
    """Root endpoint with welcome message."""
    return {
        "system": SYSTEM_NAME,
        "status": "ONLINE",
        "message": "GOOD MORNING, CREW. INTERFACE READY.",
        "docs": "/docs",
    }
