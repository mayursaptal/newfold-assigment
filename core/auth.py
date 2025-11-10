"""Authentication and authorization.

This module provides JWT-based authentication and authorization functions
for FastAPI endpoints. It includes token validation, user extraction, and
custom token verification for specific endpoints.

Example:
    ```python
    from fastapi import Depends
    from core.auth import get_current_user

    @router.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        return {"user_id": user["user_id"]}
    ```
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Callable, Awaitable
from core.settings import settings
from core.logging import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


def create_token_guard(
    token_validator: Optional[Callable[[str], Awaitable[bool]]] = None,
    token_prefix: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Callable:
    """Create a reusable token guard function for dependency injection.

    This factory function creates a token guard that can be shared across
    multiple endpoints. It supports custom validation logic, prefix checking,
    and custom error messages.

    Args:
        token_validator: Optional async function that takes a token string
            and returns True if valid, False otherwise
        token_prefix: Optional string prefix that token must start with
        error_message: Optional custom error message for invalid tokens

    Returns:
        Callable: FastAPI dependency function for token validation

    Example:
        ```python
        # Create a guard that requires 'dvd_' prefix
        dvd_token_guard = create_token_guard(token_prefix="dvd_")

        # Use in route
        @router.post("/rentals")
        async def create_rental(
            token: dict = Depends(dvd_token_guard)
        ):
            pass
        ```
    """

    async def token_guard(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> dict:
        """Token guard dependency function.

        Validates the bearer token based on the configured validation rules.

        Args:
            credentials: HTTP bearer token credentials from request header

        Returns:
            dict: Token information dictionary containing:
                - token: The validated token string
                - valid: Boolean indicating token is valid

        Raises:
            HTTPException: If token validation fails
        """
        token = credentials.credentials

        # Check prefix if specified
        if token_prefix and not token.startswith(token_prefix):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message or f"Token must start with '{token_prefix}' prefix",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Run custom validator if provided
        if token_validator:
            is_valid = await token_validator(token)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_message or "Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return {"token": token, "valid": True}

    return token_guard


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate bearer token and return current user.

    Validates a JWT bearer token and extracts user information from
    the token payload. The token must be signed with the application's
    secret key.

    Args:
        credentials: HTTP bearer token credentials from request header

    Returns:
        dict: User information dictionary containing:
            - user_id: User identifier from token 'sub' claim
            - payload: Full JWT payload

    Raises:
        HTTPException: If token is invalid, expired, or missing 'sub' claim

    Example:
        ```python
        @router.get("/profile")
        async def get_profile(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
        ```
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "payload": payload}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Create shared token guard for 'dvd_' prefix requirement
verify_dvd_token = create_token_guard(
    token_prefix="dvd_", error_message="Token must start with 'dvd_' prefix"
)


def create_access_token(data: dict) -> str:
    """Create a JWT access token.

    Encodes the provided data into a JWT token signed with the
    application's secret key using HS256 algorithm.

    Args:
        data: Dictionary of claims to encode in the token.
            Typically includes 'sub' (subject/user_id) and 'exp' (expiration)

    Returns:
        str: Encoded JWT token string

    Example:
        ```python
        token = create_access_token({
            "sub": "user123",
            "exp": datetime.utcnow() + timedelta(hours=1)
        })
        ```
    """
    return jwt.encode(data, settings.secret_key, algorithm="HS256")  # type: ignore[no-any-return]
