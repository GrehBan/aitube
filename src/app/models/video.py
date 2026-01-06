# File: src/app/models/video.py
# Description: Video and Interaction models

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Float, Enum, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from src.app.models.base import Base
import enum
import uuid

if TYPE_CHECKING:
    from src.app.models.user import User, Channel
    
class VideoStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"

class Video(Base):
    __tablename__ = "videos"

    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("channels.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String)
    
    # Storage & Playback
    original_filename: Mapped[str] = mapped_column(String)
    storage_path: Mapped[str] = mapped_column(String) # MinIO path
    hls_manifest_path: Mapped[Optional[str]] = mapped_column(String) # .m3u8 path
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String)
    
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    views: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus), default=VideoStatus.PENDING)
    
    # Search
    search_vector: Mapped[str] = mapped_column(TSVECTOR, deferred=True)

    channel: Mapped["Channel"] = relationship("Channel", back_populates="videos")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="video")
    
    __table_args__ = (
        Index('ix_videos_search_vector', 'search_vector', postgresql_using='gin'),
    )

class Comment(Base):
    __tablename__ = "comments"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("videos.id"))
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("comments.id"), nullable=True)
    content: Mapped[str] = mapped_column(String)

    user: Mapped["User"] = relationship("User")
    video: Mapped["Video"] = relationship("Video", back_populates="comments")
    replies: Mapped[List["Comment"]] = relationship("Comment", remote_side="[Comment.id]")