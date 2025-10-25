import datetime
from typing import Optional, Literal, Union, List
from pydantic import field_validator
from .base import BaseModel, DefaultPageParams

class TagOut(BaseModel):
    id: str
    name: str

class ConversationCreateIn(BaseModel):
    title: str
    tag_ids: Optional[List[str]] = None


class ConversationCreateOut(BaseModel):
    id: str
    user_id: str
    title: str
    is_group: bool
    create_date: datetime.datetime


class ConversationOut(BaseModel):
    id: str
    user_id: str
    title: str
    is_group: bool
    create_date: datetime.datetime
    tags: List[TagOut]


class ConversationUpdateIn(BaseModel):
    title: Optional[str] = None


class PersonalMsgIn(BaseModel):
    content: str


class ConversationMessageOut(BaseModel):
    id: str
    type: str
    name: str
    content: str
    data: Optional[str]
    status: str
    create_date: datetime.datetime


class PersonalConversationPageParams(DefaultPageParams):
    tag_ids: Optional[str]


