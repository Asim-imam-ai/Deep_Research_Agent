"""Application-wide API key guard; health endpoint remains public."""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from research_assistant.core.security import authenticate_api_key

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str | None = Security(api_key_header)) -> None:
    if not authenticate_api_key(key):
        raise HTTPException(
            status_code=401, detail="Valid API key required", headers={"WWW-Authenticate": "ApiKey"}
        )
