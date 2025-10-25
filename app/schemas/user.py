import datetime
from typing import Optional, Literal, Union
from pydantic import field_validator
from .base import BaseModel


class CurrentUser(BaseModel):
    id: str


class UserOut(BaseModel):
    id: str
    username: str
    name: str
    email: str


class UserCreateIn(BaseModel):
    username: str
    password: str
    name: str
    email: Optional[str] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    username: str
    password: str
