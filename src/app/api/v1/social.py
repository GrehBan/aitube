# File: src/app/api/v1/social.py
# Description: Comments and Subscriptions

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.app.api import deps
from src.app.models.user import User, Subscription, Channel
from src.app.models.video import Video, Comment
from src.app.schemas.comment import CommentCreate, CommentResponse
import uuid

router = APIRouter()

# Comments
@router.post("/videos/{video_id}/comments", response_model=CommentResponse)
async def create_comment(
    video_id: uuid.UUID,
    comment_in: CommentCreate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    comment = Comment(
        user_id=current_user.id,
        video_id=video_id,
        content=comment_in.content,
        parent_id=comment_in.parent_id
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment

@router.get("/videos/{video_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    video_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    result = await db.execute(select(Comment).where(Comment.video_id == video_id).order_by(Comment.created_at.desc()))
    return result.scalars().all()

# Subscriptions
@router.post("/channels/{channel_id}/subscribe")
async def toggle_subscription(
    channel_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    query = select(Subscription).where(
        Subscription.subscriber_id == current_user.id,
        Subscription.channel_id == channel_id
    )
    result = await db.execute(query)
    sub = result.scalars().first()

    if sub:
        await db.delete(sub)
        msg = "Unsubscribed"
    else:
        new_sub = Subscription(subscriber_id=current_user.id, channel_id=channel_id)
        db.add(new_sub)
        msg = "Subscribed"
    
    await db.commit()
    return {"message": msg}