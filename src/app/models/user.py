# File: src/app/models/user.py
# Description: User and Subscription models
import uuid

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.app.models.base import Base
if TYPE_CHECKING:
    from src.app.models.video import Video

class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    channel: Mapped[Optional["Channel"]] = relationship("Channel", back_populates="user", uselist=False)
    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="subscriber")

class Channel(Base):
    __tablename__ = "channels"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    handle: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String)
    avatar_url: Mapped[Optional[str]] = mapped_column(String)
    
    user: Mapped["User"] = relationship("User", back_populates="channel")
    videos: Mapped[List["Video"]] = relationship("Video", back_populates="channel")
    subscribers: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="channel")

class Subscription(Base):
    __tablename__ = "subscriptions"

    subscriber_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("channels.id"))

    subscriber: Mapped["User"] = relationship("User", back_populates="subscriptions")
    channel: Mapped["Channel"] = relationship("Channel", back_populates="subscribers")