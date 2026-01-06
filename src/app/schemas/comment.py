# File: src/app/schemas/comment.py
# Description: Comment schemas

from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[uuid.UUID] = None

class CommentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: datetime
    # Nested comments omitted for depth control in simple schema