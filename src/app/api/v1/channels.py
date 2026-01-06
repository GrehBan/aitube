# File: src/app/api/v1/channels.py
# Description: Channel Management Endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.app.api import deps
from src.app.models.user import User, Channel
from src.app.schemas.user import ChannelCreate, ChannelResponse
from typing import Any

router = APIRouter()

@router.post("/", response_model=ChannelResponse)
async def create_channel(
    channel_in: ChannelCreate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Create a new channel for the current user.
    """
    if current_user.channel:
        raise HTTPException(
            status_code=400,
            detail="User already has a channel"
        )
    
    # Check handle uniqueness
    result = await db.execute(select(Channel).where(Channel.handle == channel_in.handle))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Channel handle already taken"
        )

    channel = Channel(
        user_id=current_user.id,
        **channel_in.model_dump()
    )
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel

@router.get("/{handle}", response_model=ChannelResponse)
async def read_channel(
    handle: str,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    result = await db.execute(select(Channel).where(Channel.handle == handle))
    channel = result.scalars().first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel