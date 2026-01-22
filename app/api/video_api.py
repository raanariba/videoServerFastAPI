from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import List

from app.services.cpu_hls_service import convert_to_hls, list_videos
from app.config.settings import HLS_VIDEO_DIR
from app.models.video_dto import VideoResponse, UploadResponse

router = APIRouter(tags=["videos"])


@router.get(
    "/",
    summary="Get Videos",
    response_model=List[VideoResponse],
    description="Devuelve la lista de videos HLS procesados al formato NestJS."
)
async def get_videos():
    """
    Forma del objeto:
    {
      "id": string,
      "originalName": string,
      "playlistUrl": string,
      "uploadedAt": string
    }
    """
    return await list_videos()


@router.post(
    "/",
    summary="Upload Video",
    response_model=UploadResponse,
    description="Sube un video, lo convierte a HLS y devuelve metadata."
)
async def upload_video(file: UploadFile = File(...)):
    return await convert_to_hls(file)


@router.get(
    "/streams/{video_id}/{filename}",
    summary="Serve HLS files",
    include_in_schema=False,
)
async def stream_video(video_id: str, filename: str):
    """
    Sirve la playlist (.m3u8) y los segmentos (.ts)
    """
    file_path = HLS_VIDEO_DIR / video_id / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    if file_path.suffix == ".m3u8":
        media_type = "application/vnd.apple.mpegurl"
    else:
        media_type = "video/MP2T"

    return FileResponse(path=file_path, media_type=media_type)
