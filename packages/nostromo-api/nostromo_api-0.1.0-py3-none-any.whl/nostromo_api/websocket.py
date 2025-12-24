"""
WebSocket handler for real-time chat.
"""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from nostromo_api.config import get_settings
from nostromo_core import ChatEngine
from nostromo_core.adapters.memory import InMemoryStore
from nostromo_core.theme import DISPLAY_NAME
from nostromo_core.theme.errors import NostromoError, format_error, get_error_for_exception

router = APIRouter(tags=["WebSocket"])

# Shared memory store
_ws_memory_store = InMemoryStore()


def get_engine():
    """Create a ChatEngine for WebSocket connections."""
    settings = get_settings()
    api_key = settings.get_llm_api_key()

    if not api_key:
        return None

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
        return None

    return ChatEngine(llm=llm, memory=_ws_memory_store)


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time bidirectional chat.

    Protocol:
    - Client sends: plain text message or JSON {"message": "..."}
    - Server sends: JSON events
        - {"type": "token", "data": "..."} - Response token
        - {"type": "done", "session_id": "..."} - Response complete
        - {"type": "error", "message": "..."} - Error occurred
        - {"type": "connected", "session_id": "..."} - Connection established
    """
    await websocket.accept()

    # Send connection confirmation
    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "message": f"{DISPLAY_NAME} INTERFACE READY.",
    })

    engine = get_engine()
    if not engine:
        await websocket.send_json({
            "type": "error",
            "message": format_error(NostromoError.PROVIDER_MISSING, provider="LLM"),
        })
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            # Parse message (support both plain text and JSON)
            try:
                parsed = json.loads(data)
                message = parsed.get("message", data)
            except json.JSONDecodeError:
                message = data

            if not message.strip():
                continue

            # Handle exit commands
            if message.lower() in ("exit", "quit", "bye"):
                await websocket.send_json({
                    "type": "goodbye",
                    "message": format_error(NostromoError.GOODBYE),
                })
                break

            # Stream response
            try:
                async for token in engine.chat_stream(session_id, message):
                    await websocket.send_json({
                        "type": "token",
                        "data": token,
                    })

                await websocket.send_json({
                    "type": "done",
                    "session_id": session_id,
                })

            except Exception as e:
                error_type, kwargs = get_error_for_exception(e)
                await websocket.send_json({
                    "type": "error",
                    "message": format_error(error_type, **kwargs),
                })

    except WebSocketDisconnect:
        pass
    finally:
        pass
