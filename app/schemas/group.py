import datetime
from typing import Optional, Literal, Union, List
from pydantic import field_validator
from .base import BaseModel


class RobotCreateIn(BaseModel):
    name: str
    personality: str
    keywords: List[str]


class GroupCreateIn(BaseModel):
    title: str
    robot_ids: List[str]
    member_user_ids: List[str]


class GroupOut(BaseModel):
    id: str
    create_date: datetime.datetime
    title: str


class UserOut(BaseModel):
    id: str
    name: str
    is_admin: bool
    joined_date: datetime.datetime


class RobotOut(BaseModel):
    id: str
    name: str


class GroupDetailOut(BaseModel):
    id: str
    title: str
    robots: List[RobotOut]
    members: List[UserOut]


class GroupMsgIn(BaseModel):
    content: str


class GroupSettings(BaseModel):
    reponse_strategy: str = "all"  # all, random, keyword


class GroupMsgOut(BaseModel):
    type: str
    name: str
    content: str

