import uuid
from datetime import datetime, timedelta, UTC
from typing import Dict, Optional

import jwt
from passlib.context import CryptContext
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.settings import get_settings

settings = get_settings()

# ------------------------------------------------------------------
# 1. Password hashing / verification
# ------------------------------------------------------------------
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


# ------------------------------------------------------------------
# 2. Access & Refresh token helpers
#    - refresh token is a long-lived JWT that also carries a session_id
#    - server keeps a list (or DB table) of valid sessions so you can
#      revoke / log-out a user by deleting the session row.
# ------------------------------------------------------------------
_session_store: Dict[str, Dict] = {}   # replace with Redis / DB in prod

def _create_token(
        sub: str,
        scope: str,
        session_id: Optional[str] = None,
        expires_delta: timedelta = timedelta(minutes=15),
        extra: Optional[Dict] = None
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": sub,
        "scope": scope,
        "iat": now,
        "exp": now + expires_delta,
    }
    if session_id:
        payload["sid"] = session_id
    if extra:
        payload.update(extra)
    return jwt.encode(
        payload,
        settings.security.jwt_secret,
        algorithm="HS384"
    )

def create_access_token(user_id: str, outlet_id: str, company_id: str, session_id: str) -> str:
    return _create_token(
        sub=user_id,
        scope="access",
        session_id=session_id,
        outlet_id=outlet_id,
        company_id=company_id,
        expires_delta=timedelta(minutes=settings.security.access_token_expire_minutes or 15)
    )

def create_refresh_token(user_id: str) -> str:
    session_id = str(uuid.uuid4())
    token = _create_token(
        sub=user_id,
        scope="refresh",
        session_id=session_id,
        expires_delta=timedelta(days=settings.security.refresh_token_expire_days or 30)
    )
    # Persist the session server-side
    _session_store[session_id] = {"user_id": user_id,"created_at": datetime.now(UTC)}
    return token


# ------------------------------------------------------------------
# 3. Token verification
# ------------------------------------------------------------------
def _decode(token: str, scope: str) -> Dict:
    try:
        payload = jwt.decode(
            token,
            settings.security.jwt_secret,
            algorithms=["HS384"]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=f"{scope} token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=f"Invalid {scope} token")

    if payload.get("scope") != scope:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=f"Token scope mismatch")

    if scope == "refresh":
        sid = payload.get("sid")
        if sid not in _session_store:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Session revoked")
    return payload


async def verify_access_token(request: Request) -> Dict:
    token = _extract_bearer(request)
    return _decode(token, scope="access")


def verify_refresh_token(refresh_token: str) -> Dict:
    payload = _decode(refresh_token, scope="refresh")
    return payload


# ------------------------------------------------------------------
# 4. Helper
# ------------------------------------------------------------------
def _extract_bearer(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    return auth.split()[1]