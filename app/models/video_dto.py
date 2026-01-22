from pydantic import BaseModel, Field
from typing import List


class VideoResponse(BaseModel):
    id: str = Field(..., example="1768927534548-costarica4k")
    originalName: str = Field(..., example="costarica4k.mp4")
    playlistUrl: str = Field(
        ..., example="/videos/streams/1768927534548-costarica4k/index.m3u8"
    )
    uploadedAt: str = Field(..., example="2026-01-20T16:49:28.074Z")


class UploadResponse(VideoResponse):
    """Mismo schema del GET pero para el POST"""
    pass
