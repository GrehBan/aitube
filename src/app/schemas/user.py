# File: src/app/schemas/user.py
# Description: User schemas

from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    
    class Config:
        from_attributes = True

class ChannelCreate(BaseModel):
    handle: str
    name: str
    description: Optional[str] = None

class ChannelResponse(ChannelCreate):
    id: uuid.UUID
    avatar_url: Optional[str] = None