import datetime
import enum
import uuid

from sqlalchemy import String, DateTime, JSON, Boolean, Enum, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    create_date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
    )

    username: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(64), nullable=True)

    conversations = relationship("Conversation", back_populates="user")
    groups = relationship("GroupMember", back_populates="user")
