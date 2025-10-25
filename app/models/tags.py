import datetime
import enum
import uuid

from sqlalchemy import String, DateTime, JSON, Boolean, Enum, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    name: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"))

    # conversation_rel = relationship("ConversationTagRel", back_populates="tag", cascade="all, delete-orphan", passive_deletes=True)
    conversations = relationship("Conversation", secondary="conversation_tag_rel", back_populates="tags", lazy="selectin")


class ConversationTagRel(Base):
    __tablename__ = "conversation_tag_rel"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    tag_id: Mapped[str] = mapped_column(String(36), ForeignKey("tags.id", ondelete="CASCADE"))
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"))

    # tag = relationship("Tag", back_populates="conversation_rel")
    # conversation = relationship("Conversation", back_populates="tag_rel")
