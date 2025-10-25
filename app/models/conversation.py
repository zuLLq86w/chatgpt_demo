import datetime
import enum
import uuid

from sqlalchemy import String, DateTime, JSON, Boolean, Enum, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


# 会话
class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)  # 标题
    is_group: Mapped[bool] = mapped_column(default=False)  # 是否群组
    group_id: Mapped[str] = mapped_column(String(36), ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)

    create_date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
    )

    user = relationship("User", back_populates="conversations")
    group = relationship("Group", back_populates="conversations")

    messages = relationship("Message", back_populates="conversation", cascade="all, delete")
    # tag_rel = relationship("ConversationTagRel", back_populates="conversation")
    tags = relationship("Tag", secondary="conversation_tag_rel", back_populates="conversations", lazy="selectin")
