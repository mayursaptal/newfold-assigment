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
from typing import Optional
from core.settings import settings
from core.logging import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


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


async def verify_dvd_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Verify Bearer token with 'dvd_' prefix requirement.
    
    Validates that a bearer token starts with the 'dvd_' prefix.
    This is used for specific endpoints that require this token format.
    
    Args:
        credentials: HTTP bearer token credentials from request header
        
    Returns:
        dict: Token information dictionary containing:
            - token: The validated token string
            - valid: Boolean indicating token is valid
            
    Raises:
        HTTPException: If token doesn't start with 'dvd_' prefix
        
    Example:
        ```python
        @router.post("/rentals")
        async def create_rental(
            token: dict = Depends(verify_dvd_token)
        ):
            # Token validated, proceed with rental creation
            pass
        ```
    """
    token = credentials.credentials
    
    if not token.startswith("dvd_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token must start with 'dvd_' prefix",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"token": token, "valid": True}


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
    return jwt.encode(data, settings.secret_key, algorithm="HS256")

