"""Error handling utilities for API routes."""

from fastapi import HTTPException, status
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar('T')


def handle_api_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle common API errors.
    Converts ValueError to 400, other exceptions to 500.
    HTTPException is allowed to propagate (not caught).
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTPException as-is (don't wrap it)
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"❌ Unhandled exception in {func.__name__}: {str(e)}")
            print(f"   Full traceback:\n{error_traceback}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}",
            )
    return wrapper

