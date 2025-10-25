import datetime
import enum
import uuid

from sqlalchemy import String, DateTime, JSON, Boolean, Enum, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base

# 群组
class Group(Base):
    __tablename__ = "groups"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    create_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    create_date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC)
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    settings: Mapped[str] = mapped_column(JSON, nullable=True)

    conversations = relationship("Conversation", back_populates="group")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete")
    robots = relationship("GroupRobotRel", back_populates="group", cascade="all, delete")


class GroupMember(Base):
    __tablename__ = "group_members"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    group_id: Mapped[str] = mapped_column(String(36), ForeignKey("groups.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_date: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now(datetime.UTC))

    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="groups")


class GroupRobot(Base):
    __tablename__ = "group_robots"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    personality: Mapped[str] = mapped_column(Text, nullable=True)
    keywords: Mapped[str] = mapped_column(Text, nullable=True)

    roles = relationship("GroupRobotRel", back_populates="robot")


class GroupRobotRel(Base):
    __tablename__ = "group_robot_rel"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    group_id: Mapped[str] = mapped_column(String(36), ForeignKey("groups.id"))
    robot_id: Mapped[str] = mapped_column(String(36), ForeignKey("group_robots.id"))
    weight: Mapped[int] = mapped_column(Integer, default=1)

    group = relationship("Group", back_populates="robots")
    robot = relationship("GroupRobot", back_populates="roles")
