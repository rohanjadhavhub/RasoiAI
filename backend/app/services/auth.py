"""
Auth0 Token Verification Service for RasoiAI
Uses PyJWT + JWKS for RS256 token signature verification
"""
import jwt
from jwt import PyJWKClient
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings

settings = get_settings()

# ---- HARD FAIL IF MISCONFIGURED ----
if not settings.auth0_domain:
    raise RuntimeError("AUTH0_DOMAIN not configured")

if not settings.auth0_api_audience:
    raise RuntimeError("AUTH0_API_AUDIENCE not configured")

if not settings.auth0_algorithms:
    raise RuntimeError("AUTH0_ALGORITHMS not configured")


# HTTP Bearer token scheme
bearer_scheme = HTTPBearer(auto_error=False)

# JWKS client — caches keys from Auth0
_jwks_client: Optional[PyJWKClient] = None


def get_jwks_client() -> PyJWKClient:
    """Get or create JWKS client (cached)"""
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify an Auth0 access token using JWKS.
    Returns the decoded token claims.
    Raises HTTPException on failure.
    """
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=settings.auth0_algorithms,  # must be ['RS256']
            audience=settings.auth0_api_audience,
            issuer=f"https://{settings.auth0_domain}/",
            options={
                "require": ["exp", "iat", "sub"],
            },
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience",
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer",
        )
    except jwt.PyJWKClientError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to fetch signing keys",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """
    Requires valid Auth0 Bearer token.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_token(credentials.credentials)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[Dict[str, Any]]:
    """
    Optionally validates Auth0 Bearer token.
    """
    if credentials is None:
        return None

    try:
        return verify_token(credentials.credentials)
    except HTTPException:
        return None


def require_role(required_role: str):
    """
    Role-based access control.
    """

    async def role_checker(
        user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:

        # Auth0 standard RBAC claim
        roles = user.get("roles", [])

        # Namespace-based role claims
        for key, value in user.items():
            if key.endswith("/roles") and isinstance(value, list):
                roles = value
                break

        if not isinstance(roles, list):
            roles = []

        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )

        return user

    return role_checker
