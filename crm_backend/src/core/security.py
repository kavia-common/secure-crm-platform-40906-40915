from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import jwt  # PyJWT
from passlib.context import CryptContext

from src.core.settings import get_settings


# Password hashing context (bcrypt)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt-hashed form."""
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _expiry(minutes: int) -> datetime:
    return _utcnow() + timedelta(minutes=minutes)


def _base_claims(
    subject: str,
    token_type: str,
    username: Optional[str] = None,
    roles: Optional[List[str]] = None,
    issuer: Optional[str] = None,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    base: Dict[str, Any] = {
        "sub": subject,
        "jti": str(uuid.uuid4()),
        "iat": int(_utcnow().timestamp()),
        "typ": token_type,
        "username": username,
        "roles": roles or [],
        "iss": issuer or "crm-backend",
    }
    # Optionally include email claim for clients that expect it (e.g., test user bypass)
    if email:
        base["email"] = email
    return base


# PUBLIC_INTERFACE
def create_access_token(
    user_id: str,
    username: str,
    roles: List[str],
    email: Optional[str] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Create a signed JWT access token with configured expiry.

    Returns tuple of (token, claims) so caller can access jti, exp, etc.
    Optionally embeds email in JWT for clients that use it.
    """
    settings = get_settings()
    claims = _base_claims(
        subject=user_id,
        token_type="access",
        username=username,
        roles=roles,
        issuer="crm-backend",
        email=email,
    )
    exp = _expiry(int(settings.ACCESS_TOKEN_EXPIRES_MIN))
    payload = {**claims, "exp": exp}
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    # PyJWT returns str for modern versions
    return token, payload


# PUBLIC_INTERFACE
def create_refresh_token(user_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Create a signed JWT refresh token with configured expiry.

    Returns tuple of (token, claims).
    """
    settings = get_settings()
    claims = _base_claims(
        subject=user_id,
        token_type="refresh",
        issuer="crm-backend",
    )
    exp = _expiry(int(settings.REFRESH_TOKEN_EXPIRES_MIN))
    payload = {**claims, "exp": exp}
    token = jwt.encode(
        payload,
        settings.JWT_REFRESH_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, payload


# PUBLIC_INTERFACE
def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate an access token. Raises jwt.InvalidTokenError on issues.
    """
    settings = get_settings()
    claims = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "sub", "jti"]},
    )
    # Minimal structural validation
    if claims.get("typ") != "access":
        raise jwt.InvalidTokenError("Invalid token type")
    return claims


# PUBLIC_INTERFACE
def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a refresh token. Raises jwt.InvalidTokenError on issues.
    """
    settings = get_settings()
    claims = jwt.decode(
        token,
        settings.JWT_REFRESH_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "sub", "jti"]},
    )
    if claims.get("typ") != "refresh":
        raise jwt.InvalidTokenError("Invalid token type")
    return claims
