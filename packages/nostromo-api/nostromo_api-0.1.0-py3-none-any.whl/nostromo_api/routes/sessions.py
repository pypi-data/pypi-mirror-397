"""
Session management routes.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from nostromo_api.auth import User, get_current_user
from nostromo_api.routes.chat import _memory_store
from nostromo_core.theme.errors import NostromoError, format_error

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


class SessionInfo(BaseModel):
    """Session information."""

    id: str
    message_count: int


class SessionListResponse(BaseModel):
    """Response for session list."""

    sessions: list[SessionInfo]
    total: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    success: bool


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    user: Annotated[User, Depends(get_current_user)],
) -> SessionListResponse:
    """
    List all sessions for the current user.
    """
    all_sessions = await _memory_store.list_sessions()

    # Filter to user's sessions
    user_prefix = f"{user.id}:"
    user_sessions = [s for s in all_sessions if s.startswith(user_prefix)]

    sessions = []
    for session_id in user_sessions:
        session = await _memory_store.get_session(session_id)
        if session:
            # Remove user prefix for display
            display_id = session_id[len(user_prefix) :]
            sessions.append(
                SessionInfo(
                    id=display_id,
                    message_count=len(session.messages),
                )
            )

    return SessionListResponse(sessions=sessions, total=len(sessions))


@router.delete("/{session_id}", response_model=MessageResponse)
async def delete_session(
    session_id: str,
    user: Annotated[User, Depends(get_current_user)],
) -> MessageResponse:
    """
    Delete a specific session.
    """
    full_session_id = f"{user.id}:{session_id}"
    deleted = await _memory_store.delete_session(full_session_id)

    if deleted:
        return MessageResponse(
            message=f"SESSION {session_id} PURGED FROM MEMORY BANKS.",
            success=True,
        )
    else:
        return MessageResponse(
            message=format_error(NostromoError.SESSION_NOT_FOUND, session_id=session_id),
            success=False,
        )


@router.delete("", response_model=MessageResponse)
async def clear_all_sessions(
    user: Annotated[User, Depends(get_current_user)],
) -> MessageResponse:
    """
    Clear all sessions for the current user.
    """
    all_sessions = await _memory_store.list_sessions()

    user_prefix = f"{user.id}:"
    count = 0

    for session_id in all_sessions:
        if session_id.startswith(user_prefix):
            await _memory_store.delete_session(session_id)
            count += 1

    return MessageResponse(
        message=f"{count} SESSION(S) PURGED FROM MEMORY BANKS.",
        success=True,
    )
