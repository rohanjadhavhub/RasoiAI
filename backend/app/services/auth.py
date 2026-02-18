"""
Auth0 Token Verification Service for RasoiAI

Supports two token types:
  1. JWT access tokens (when a custom API audience is configured)
  2. Opaque access tokens (when using Auth0 Management API audience)
     → validated via Auth0's /userinfo endpoint
"""
import logging
import jwt
from jwt import PyJWKClient
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
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

# Auth0 userinfo URL for opaque token validation
USERINFO_URL = f"https://{settings.auth0_domain}/userinfo"


def get_jwks_client() -> PyJWKClient:
    """Get or create JWKS client (cached)"""
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


def _is_jwt(token: str) -> bool:
    """Check if a token looks like a JWT (three base64 segments)."""
    return token.count(".") == 2


def _verify_jwt(token: str) -> Dict[str, Any]:
    """
    Verify a JWT access token using JWKS.
    Returns decoded claims.
    """
    jwks_client = get_jwks_client()
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=settings.auth0_algorithms,
        audience=settings.auth0_api_audience,
        issuer=f"https://{settings.auth0_domain}/",
        options={
            "require": ["exp", "iat", "sub"],
        },
    )
    return payload


async def _verify_opaque_token(token: str) -> Dict[str, Any]:
    """
    Validate an opaque access token by calling Auth0's /userinfo endpoint.
    Auth0 validates the token and returns user profile claims.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {token}"},
        )

    if resp.status_code == 200:
        data = resp.json()
        # Normalize to match JWT claim format
        return {
            "sub": data.get("sub", ""),
            "email": data.get("email"),
            "name": data.get("name"),
            "nickname": data.get("nickname"),
            "picture": data.get("picture"),
            "email_verified": data.get("email_verified", False),
        }
    elif resp.status_code == 401:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired or is invalid",
        )
    else:
        logger.error(f"Auth0 /userinfo returned {resp.status_code}: {resp.text}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to validate token with Auth0",
        )


async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify an Auth0 access token.
    - If it's a JWT, verify locally using JWKS.
    - If it's opaque, validate via Auth0 /userinfo endpoint.
    """
    if _is_jwt(token):
        try:
            return _verify_jwt(token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except jwt.InvalidAudienceError:
            # Audience mismatch — might be an opaque-like JWT; fall through
            logger.warning("JWT audience mismatch, trying /userinfo fallback")
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
            # Token looks like JWT but can't be decoded — try /userinfo
            logger.warning("JWT decode failed, trying /userinfo fallback")

    # Opaque token or JWT fallback — validate via Auth0
    return await _verify_opaque_token(token)


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

    return await verify_token(credentials.credentials)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[Dict[str, Any]]:
    """
    Optionally validates Auth0 Bearer token.
    """
    if credentials is None:
        return None

    try:
        return await verify_token(credentials.credentials)
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
