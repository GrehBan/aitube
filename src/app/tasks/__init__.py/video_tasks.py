# File: src/app/tasks/video_tasks.py
# Description: Video processing logic

from src.app.tasks.worker import celery_app
from src.app.database import AsyncSessionLocal
from src.app.models.video import Video, VideoStatus
from src.app.services.storage import storage
from src.app.config import settings
import ffmpeg
import os
import uuid
import asyncio
import logging
from sqlalchemy import select

logger = logging.getLogger(__name__)

async def update_video_status(video_id: uuid.UUID, status: VideoStatus, hls_path: str = None, duration: float = 0.0):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalars().first()
        if video:
            video.status = status
            if hls_path:
                video.hls_manifest_path = hls_path
            if duration > 0:
                video.duration = duration
            await db.commit()

@celery_app.task
def process_video_upload(video_id_str: str, input_path: str):
    video_id = uuid.UUID(video_id_str)
    output_dir = f"/tmp/{video_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Probe video
        probe = ffmpeg.probe(input_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        duration = float(probe['format']['duration'])

        # HLS Conversion
        hls_output = f"{output_dir}/index.m3u8"
        (
            ffmpeg
            .input(input_path)
            .output(hls_output, format='hls', hls_time=10, hls_list_size=0, hls_flags='delete_segments')
            .run(capture_stdout=True, capture_stderr=True)
        )

        # Upload to MinIO
        minio_base = f"videos/{video_id}"
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            object_name = f"{minio_base}/{filename}"
            content_type = "application/x-mpegURL" if filename.endswith(".m3u8") else "video/MP2T"
            storage.upload_file(file_path, object_name, content_type)

        # Cleanup
        os.remove(input_path)
        for f in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, f))
        os.rmdir(output_dir)

        # Update DB (Need to run async in sync celery)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            update_video_status(
                video_id, 
                VideoStatus.PUBLISHED, 
                f"{minio_base}/index.m3u8",
                duration
            )
        )
        logger.info(f"Video {video_id} processed successfully")

    except Exception as e:
        logger.error(f"Processing failed for {video_id}: {e}")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(update_video_status(video_id, VideoStatus.FAILED))