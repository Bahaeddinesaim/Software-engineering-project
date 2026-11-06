"""API key security with fail-closed configuration."""

import secrets
from typing import Annotated

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(request: Request, key: Annotated[str | None, Security(key_header)]) -> None:
    """Reject absent or incorrect credentials without logging their contents."""
    configured = request.app.state.settings.api_key
    if configured is None:
        raise HTTPException(503, "API authentication is not configured")
    if key is None or not secrets.compare_digest(
        key.encode(), configured.get_secret_value().encode()
    ):
        raise HTTPException(401, "Invalid API key")
