# File: src/app/services/search.py
# Description: Full Text Search Service

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from src.app.models.video import Video, VideoStatus
from typing import List

async def search_videos(db: AsyncSession, query_str: str, limit: int = 20) -> List[Video]:
    """
    Executes a Full Text Search using PostgreSQL's websearch_to_tsquery.
    Rank results by relevance (ts_rank).
    """
    if not query_str:
        return []

    # Using raw SQL fragment for TS operations within SQLAlchemy
    # Note: Ensure the search_vector column is populated via triggers or app logic
    stmt = (
        select(Video)
        .where(
            Video.status == VideoStatus.PUBLISHED,
            text("search_vector @@ websearch_to_tsquery('english', :q)")
        )
        .order_by(text("ts_rank(search_vector, websearch_to_tsquery('english', :q)) DESC"))
        .limit(limit)
    )
    
    result = await db.execute(stmt, {"q": query_str})
    return list(result.scalars().all())

async def update_search_vector(db: AsyncSession, video_id: str):
    """
    Manually update search vector if triggers aren't used.
    concatenates title and description.
    """
    stmt = text("""
        UPDATE videos 
        SET search_vector = to_tsvector('english', title || ' ' || coalesce(description, ''))
        WHERE id = :id
    """)
    await db.execute(stmt, {"id": video_id})
    await db.commit()