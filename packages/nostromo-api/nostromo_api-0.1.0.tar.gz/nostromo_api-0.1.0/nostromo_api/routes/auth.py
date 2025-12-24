"""
Authentication routes.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from nostromo_api.auth import Token, create_access_token
from nostromo_api.config import Settings, get_settings
from nostromo_core.theme.errors import NostromoError, format_error

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Login request body."""

    username: str
    password: str


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Token:
    """
    Get an access token for API authentication.

    For demo purposes, accepts any username/password.
    In production, implement proper user authentication.
    """
    # In production, validate credentials against a user store
    # For demo, we accept any credentials
    if not form_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(NostromoError.AUTH_FAILED),
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": form_data.username},
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return Token(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout")
async def logout() -> dict:
    """
    Logout endpoint.

    For JWT, client should discard the token.
    This endpoint is provided for API completeness.
    """
    return {
        "message": format_error(NostromoError.GOODBYE),
        "success": True,
    }
