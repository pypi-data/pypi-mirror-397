"""
Authentication handlers for JWT and API Key.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from nostromo_api.config import Settings, get_settings
from nostromo_core.theme.errors import NostromoError, format_error

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# JWT settings
ALGORITHM = "HS256"


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Data encoded in JWT."""

    sub: str  # Subject (user identifier)
    exp: datetime
    iat: datetime


class User(BaseModel):
    """User model for authentication."""

    id: str
    username: str
    is_active: bool = True


def create_access_token(
    data: dict,
    settings: Settings,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in token
        settings: Application settings
        expires_delta: Optional custom expiration

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def verify_token(token: str, settings: Settings) -> TokenData | None:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string
        settings: Application settings

    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return TokenData(
            sub=payload.get("sub", ""),
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc),
            iat=datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc),
        )
    except JWTError:
        return None


def verify_api_key(api_key: str, settings: Settings) -> bool:
    """
    Verify an API key.

    Args:
        api_key: API key to verify
        settings: Application settings

    Returns:
        True if valid, False otherwise
    """
    # Check if key starts with expected prefix
    if not api_key.startswith("nst_"):
        return False

    # Check against configured keys
    return api_key in settings.valid_api_keys


async def get_current_user(
    bearer: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)],
    api_key: Annotated[str | None, Security(api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """
    Get the current authenticated user.

    Supports both JWT Bearer tokens and API keys.

    Args:
        bearer: Bearer token from Authorization header
        api_key: API key from X-API-Key header
        settings: Application settings

    Returns:
        User object

    Raises:
        HTTPException: If authentication fails
    """
    # Try API key first
    if api_key:
        if verify_api_key(api_key, settings):
            return User(id="api-key-user", username="api")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(NostromoError.AUTH_FAILED),
            headers={"WWW-Authenticate": "Bearer, ApiKey"},
        )

    # Try JWT token
    if bearer:
        token_data = verify_token(bearer.credentials, settings)
        if token_data:
            return User(id=token_data.sub, username=token_data.sub)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_error(NostromoError.SESSION_EXPIRED),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # No authentication provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=format_error(NostromoError.NO_AUTH),
        headers={"WWW-Authenticate": "Bearer, ApiKey"},
    )


async def get_optional_user(
    bearer: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)],
    api_key: Annotated[str | None, Security(api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User | None:
    """
    Get user if authenticated, None otherwise.

    Same as get_current_user but doesn't raise on missing auth.
    """
    try:
        return await get_current_user(bearer, api_key, settings)
    except HTTPException:
        return None
