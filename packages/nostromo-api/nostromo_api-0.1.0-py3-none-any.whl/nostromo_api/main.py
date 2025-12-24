"""
MU-TH-UR 6000 REST API Server.

FastAPI application with Aliens-themed chat endpoints.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from nostromo_api.config import get_settings
from nostromo_api.errors import general_exception_handler, http_exception_handler
from nostromo_api.routes import auth_router, chat_router, health_router, sessions_router
from nostromo_api.websocket import router as websocket_router
from nostromo_core.theme import HEADER_COMPACT, SYSTEM_NAME

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=SYSTEM_NAME,
    description=f"""
{HEADER_COMPACT}

**MU-TH-UR 6000 REST API**

A retro-styled chatbot API inspired by the Aliens film franchise.

## Authentication

Two methods are supported:

1. **JWT Bearer Token**: Use `/api/auth/token` to obtain a token
2. **API Key**: Set `X-API-Key` header with a valid key (prefix: `nst_`)

## Streaming

Use `/api/chat/stream` for Server-Sent Events (SSE) streaming responses.

## WebSocket

Connect to `/ws/chat/{{session_id}}` for real-time bidirectional chat.
""",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(websocket_router)


def run():
    """Run the API server."""
    uvicorn.run(
        "nostromo_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
