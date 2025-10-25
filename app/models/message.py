import datetime
import enum
import uuid
from typing import Optional

from sqlalchemy import String, DateTime, JSON, Boolean, Enum, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class MessageStatus(enum.Enum):
    ok = "ok"
    error = "error"
    pending = "pending"


class MessageType(enum.Enum):
    user = "user"
    system = "system"
    robot = "robot"


#  消息记录
class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey('conversations.id', ondelete="CASCADE"))  # 会话id
    type: Mapped[str] = mapped_column(Enum(MessageType), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=True)  # user.name or robot.name

    content: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(Enum(MessageStatus), default=MessageStatus.ok)
    create_date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
    )

    conversation = relationship("Conversation", back_populates="messages")

