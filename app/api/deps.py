from contextlib import AbstractAsyncContextManager
from typing import Annotated, Callable, AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core.config import settings
from app.core import auth
from app.schemas.user import CurrentUser

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"/api/login")


TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(
    token: TokenDep,
) -> CurrentUser:
    # TODO：需要从redis中校验是否有效
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[auth.ALGORITHM]
        )
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    return CurrentUser(id=payload["sub"])

