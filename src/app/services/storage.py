# File: src/app/services/storage.py
# Description: MinIO interaction layer

from minio import Minio
from src.app.config import settings
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(settings.MINIO_BUCKET):
            self.client.make_bucket(settings.MINIO_BUCKET)

    def get_presigned_upload_url(self, object_name: str) -> str:
        return self.client.presigned_put_object(
            settings.MINIO_BUCKET, object_name
        )

    def upload_file(self, file_path: str, object_name: str, content_type: str):
        try:
            self.client.fput_object(settings.MINIO_BUCKET, object_name, file_path, content_type=content_type)
        except Exception as e:
            logger.error(f"Failed to upload {object_name}: {e}")
            raise e

storage = StorageService()