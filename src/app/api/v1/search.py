# File: src/app/api/v1/search.py
# Description: Search & Discovery Router

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.api import deps
from src.app.services.search import search_videos
from src.app.services.recommendation import get_trending_videos
from src.app.schemas.video import VideoResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[VideoResponse])
async def search(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Search videos by title and description using Full Text Search.
    """
    return await search_videos(db, q)

@router.get("/trending", response_model=List[VideoResponse])
async def trending(
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Get top trending videos based on views.
    """
    return await get_trending_videos(db)