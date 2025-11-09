"""Authentication and authorization."""

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
    """
    Validate bearer token and return current user.
    
    Args:
        credentials: HTTP bearer token credentials
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If token is invalid or missing
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
    """
    Verify Bearer token with 'dvd_' prefix requirement.
    
    Args:
        credentials: HTTP bearer token credentials
        
    Returns:
        Token information dictionary
        
    Raises:
        HTTPException: If token is invalid or doesn't start with 'dvd_'
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
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        
    Returns:
        Encoded JWT token
    """
    return jwt.encode(data, settings.secret_key, algorithm="HS256")

