# File: src/app/services/recommendation.py
# Description: Recommendation Engine Logic

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from src.app.models.video import Video, VideoStatus
from typing import List

async def get_trending_videos(db: AsyncSession, limit: int = 10) -> List[Video]:
    """
    Returns videos with the highest view count.
    """
    stmt = (
        select(Video)
        .where(Video.status == VideoStatus.PUBLISHED)
        .order_by(desc(Video.views))
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_related_videos(db: AsyncSession, video_id: str, limit: int = 5) -> List[Video]:
    """
    Returns videos from the same channel or with similar titles.
    Currently implements 'Same Channel' logic for MVP efficiency.
    """
    # Get current video to find channel_id
    current_vid = await db.get(Video, video_id)
    if not current_vid:
        return []

    stmt = (
        select(Video)
        .where(
            Video.channel_id == current_vid.channel_id,
            Video.id != video_id,
            Video.status == VideoStatus.PUBLISHED
        )
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())