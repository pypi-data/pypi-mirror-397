"""Rate limiting service using slowapi."""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from ai_startup_diagnosis.config import settings


def get_api_key_for_rate_limit(request: Request) -> str:
    """
    Get API key from request for rate limiting.
    Uses API key if available, otherwise falls back to IP address.
    """
    # Try to get API key from headers
    api_key = request.headers.get("x-api-key")
    if api_key:
        return f"api_key:{api_key}"
    
    # Try Authorization header
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        api_key = auth_header.replace("Bearer ", "").strip()
        if api_key:
            return f"api_key:{api_key}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Initialize rate limiter
limiter = Limiter(
    key_func=get_api_key_for_rate_limit,
    default_limits=[f"{settings.rate_limit_per_hour}/hour", f"{settings.rate_limit_per_minute}/minute"],
    storage_uri="memory://",  # In-memory storage (use Redis for production)
)

# Export rate limit exceeded handler
rate_limit_exceeded_handler = _rate_limit_exceeded_handler

