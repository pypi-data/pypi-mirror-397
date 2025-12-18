"""API key authentication for FastAPI."""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ai_startup_diagnosis.config import settings
from typing import Optional

# Use auto_error=False to allow OPTIONS requests to pass through without requiring auth
security = HTTPBearer(auto_error=False)


async def get_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Dependency to validate API key from request headers.
    
    Supports two methods:
    1. X-API-Key header
    2. Authorization: Bearer <key> header
    
    Args:
        request: FastAPI request object
        credentials: HTTP Bearer token from Authorization header (optional)
        
    Returns:
        Validated API key string
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    # Allow OPTIONS requests to pass through (CORS preflight)
    if request.method == "OPTIONS":
        return ""
    
    # Get API key from X-API-Key header or Authorization header
    api_key = None
    
    # Try X-API-Key header first
    if "x-api-key" in request.headers:
        api_key = request.headers.get("x-api-key")
    # Try Authorization Bearer token
    elif credentials:
        api_key = credentials.credentials
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide API key via X-API-Key header or Authorization: Bearer <key>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate API key
    valid_keys = settings.get_valid_api_keys()
    
    # If no API keys are configured, allow any key (development mode)
    if not valid_keys:
        if settings.debug:
            return api_key
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API keys not configured. Please set API_KEYS environment variable.",
            )
    
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key

