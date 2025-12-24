# nostromo-api

MU-TH-UR 6000 REST API - FastAPI server for the Aliens-themed chatbot.

## Installation

```bash
# With Anthropic (recommended)
pip install "nostromo-api[anthropic]"

# With OpenAI
pip install "nostromo-api[openai]"

# All providers
pip install "nostromo-api[all]"
```

## Quick Start

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Run the server
nostromo-api

# Or with uvicorn directly
uvicorn nostromo_api.main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message, get full response |
| POST | `/api/chat/stream` | SSE streaming response |
| WS | `/ws/chat/{session_id}` | WebSocket bidirectional chat |
| POST | `/api/auth/token` | Get JWT token (login) |
| GET | `/api/sessions` | List user sessions |
| DELETE | `/api/sessions/{id}` | Delete session |
| GET | `/health` | Health check |
| GET | `/docs` | OpenAPI documentation |

## Authentication

Supports two authentication methods:

1. **JWT Token** (for web apps):
   ```
   Authorization: Bearer <token>
   ```

2. **API Key** (for integrations):
   ```
   X-API-Key: nst_<your-api-key>
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `NOSTROMO_SECRET_KEY` | JWT signing key | Random |
| `NOSTROMO_API_KEYS` | Comma-separated API keys | - |
| `NOSTROMO_PROVIDER` | Default provider | anthropic |
| `NOSTROMO_MODEL` | Default model | claude-3-5-haiku-latest |
