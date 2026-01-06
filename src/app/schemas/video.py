# File: src/app/schemas/video.py
# Description: Video schemas

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from src.app.models.video import VideoStatus

class VideoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class VideoResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    hls_manifest_path: Optional[str]
    thumbnail_path: Optional[str]
    views: int
    status: VideoStatus
    created_at: datetime
    
    class Config:
        from_attributes = True