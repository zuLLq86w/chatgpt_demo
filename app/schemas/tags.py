import datetime
from typing import Optional, Literal, Union
from pydantic import field_validator
from .base import BaseModel


class TagCreateIn(BaseModel):
    name: str


class TagCreateOut(BaseModel):
    id: str
    name: str


class TagOut(BaseModel):
    id: str
    name: str
