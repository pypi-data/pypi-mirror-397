"""
Themed error handlers for the API.

Maps exceptions to MU-TH-UR 6000 themed responses.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from nostromo_core.theme import SYSTEM_NAME
from nostromo_core.theme.errors import NostromoError, format_error, get_error_for_exception


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    code: str
    system: str = SYSTEM_NAME


def create_error_response(
    error: NostromoError,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    **kwargs,
) -> JSONResponse:
    """Create a themed error response."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=format_error(error, **kwargs),
            code=error.name,
        ).model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with themed messages."""
    # Map common status codes to themed errors
    error_map = {
        status.HTTP_401_UNAUTHORIZED: NostromoError.AUTH_FAILED,
        status.HTTP_403_FORBIDDEN: NostromoError.PERMISSION_DENIED,
        status.HTTP_404_NOT_FOUND: NostromoError.SESSION_NOT_FOUND,
        status.HTTP_429_TOO_MANY_REQUESTS: NostromoError.RATE_LIMITED,
        status.HTTP_500_INTERNAL_SERVER_ERROR: NostromoError.PROCESSING_ERROR,
        status.HTTP_503_SERVICE_UNAVAILABLE: NostromoError.UPLINK_FAILURE,
    }

    # Use the exception detail if it's already themed, otherwise map
    if isinstance(exc.detail, str) and any(
        phrase in exc.detail
        for phrase in ["MU-TH-UR", "AUTHORIZATION", "UPLINK", "INTERFACE"]
    ):
        # Already a themed message
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.detail,
                code="THEMED_ERROR",
            ).model_dump(),
        )

    # Map to themed error
    error = error_map.get(exc.status_code, NostromoError.PROCESSING_ERROR)
    kwargs = {}

    if error == NostromoError.RATE_LIMITED:
        kwargs["seconds"] = "60"
    elif error == NostromoError.SESSION_NOT_FOUND:
        kwargs["session_id"] = "UNKNOWN"

    return create_error_response(error, exc.status_code, **kwargs)


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions with themed messages."""
    error, kwargs = get_error_for_exception(exc)
    return create_error_response(error, status.HTTP_500_INTERNAL_SERVER_ERROR, **kwargs)


class NostromoHTTPException(HTTPException):
    """Custom HTTP exception with themed error."""

    def __init__(
        self,
        error: NostromoError,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        **kwargs,
    ):
        super().__init__(
            status_code=status_code,
            detail=format_error(error, **kwargs),
        )
        self.error = error
        self.error_kwargs = kwargs
