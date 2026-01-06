# File: src/app/api/v1/videos.py
# Description: Video endpoints

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.api import deps
from src.app.models.user import User
from src.app.models.video import Video, VideoStatus
from src.app.schemas.video import VideoResponse
from src.app.tasks.video_tasks import process_video_upload
import shutil
import uuid
import os
from sqlalchemy import select

router = APIRouter()

@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    if not current_user.channel:
        raise HTTPException(status_code=400, detail="Create a channel first")

    # Save temp file (Basic impl, chunked usually handled by frontend JS logic combining slices)
    file_id = uuid.uuid4()
    temp_path = f"/tmp/{file_id}_{file.filename}"
    
    # Needs aiofiles for true async file write, but using shutil for brevity in prototype
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_video = Video(
        id=file_id,
        channel_id=current_user.channel.id,
        title=title,
        description=description,
        original_filename=file.filename,
        storage_path="", # Set after processing
        status=VideoStatus.PROCESSING
    )
    db.add(db_video)
    await db.commit()
    await db.refresh(db_video)

    # Trigger Celery
    process_video_upload.delay(str(file_id), temp_path)

    return db_video

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video