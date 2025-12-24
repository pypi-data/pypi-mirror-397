"""
Chat API routes.

REST and SSE endpoints for chat functionality.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from nostromo_api.auth import User, get_current_user
from nostromo_api.config import Settings, get_settings
from nostromo_api.errors import NostromoHTTPException
from nostromo_core import ChatEngine
from nostromo_core.adapters.memory import InMemoryStore
from nostromo_core.theme import DISPLAY_NAME
from nostromo_core.theme.errors import NostromoError

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# In-memory store for API (could be Redis in production)
_memory_store = InMemoryStore()


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=32000)
    session_id: str = Field(default="default", max_length=100)


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    response: str
    session_id: str
    provider: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)
    assistant_name: str = DISPLAY_NAME


def get_engine(settings: Settings) -> ChatEngine:
    """
    Create a ChatEngine with configured provider.

    Args:
        settings: Application settings

    Returns:
        Configured ChatEngine instance
    """
    api_key = settings.get_llm_api_key()
    if not api_key:
        raise NostromoHTTPException(
            NostromoError.KEY_MISSING,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            provider=settings.provider.upper(),
        )

    # Create LLM provider
    if settings.provider == "anthropic":
        from nostromo_core.adapters.anthropic import AnthropicProvider

        llm = AnthropicProvider(
            api_key=api_key,
            model=settings.model,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )
    elif settings.provider == "openai":
        from nostromo_core.adapters.openai import OpenAIProvider

        llm = OpenAIProvider(
            api_key=api_key,
            model=settings.model,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )
    else:
        raise NostromoHTTPException(
            NostromoError.INVALID_PROVIDER,
            status_code=status.HTTP_400_BAD_REQUEST,
            provider=settings.provider.upper(),
        )

    return ChatEngine(llm=llm, memory=_memory_store)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChatResponse:
    """
    Send a chat message and receive a complete response.

    Requires authentication via JWT token or API key.
    """
    engine = get_engine(settings)

    # Use user-specific session ID
    session_id = f"{user.id}:{request.session_id}"

    try:
        result = await engine.chat(session_id, request.message)
        return ChatResponse(
            response=result.message.content,
            session_id=request.session_id,
            provider=result.provider,
            model=result.model,
            usage=result.usage,
        )
    except Exception as e:
        raise NostromoHTTPException(
            NostromoError.PROCESSING_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> EventSourceResponse:
    """
    Send a chat message and receive a streaming response via SSE.

    Events:
    - `token`: A token chunk of the response
    - `done`: Streaming complete
    - `error`: An error occurred
    """
    engine = get_engine(settings)
    session_id = f"{user.id}:{request.session_id}"

    async def event_generator():
        try:
            async for token in engine.chat_stream(session_id, request.message):
                yield {"event": "token", "data": token}
            yield {"event": "done", "data": ""}
        except Exception as e:
            from nostromo_core.theme.errors import get_error_for_exception

            error_type, kwargs = get_error_for_exception(e)
            from nostromo_core.theme.errors import format_error

            error_msg = format_error(error_type, **kwargs)
            yield {"event": "error", "data": error_msg}

    return EventSourceResponse(event_generator())
