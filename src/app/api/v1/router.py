# File: src/app/api/v1/router.py
# Description: Main API Router

from fastapi import APIRouter
from src.app.api.v1 import auth, videos, social

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(social.router, tags=["social"])