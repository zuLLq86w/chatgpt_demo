from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from passlib.apps import custom_app_context as pwd_context

from .config import settings


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    if not expires_delta:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"exp": expire, "sub": str(subject)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(str(password))


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None
