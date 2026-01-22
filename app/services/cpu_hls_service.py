import json
import time
import re
import os
import subprocess
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config.settings import (
    RAW_VIDEO_DIR,
    HLS_VIDEO_DIR,
    HLS_PLAYLIST,
    ensure_upload_folders,
)


def generate_video_folder(name: str) -> str:
    base = re.sub(r'[^a-zA-Z0-9]+', '', name.split('.')[0].lower())
    uid = str(int(time.time() * 1000))
    return f"{uid}-{base}"


def print_progress(line: str, duration: float):
    if "out_time_ms=" in line:
        try:
            out_ms = int(line.replace("out_time_ms=", "").strip())
            pct = (out_ms / (duration * 1_000_000)) * 100
            pct = min(100, pct)
            print(f"[VideoService] Processing: {pct:.0f}%")
        except:
            pass


async def convert_to_hls(file: UploadFile) -> dict:
    ensure_upload_folders()

    if not file.filename:
        raise HTTPException(status_code=400, detail="Archivo inválido")

    original_name = file.filename
    ext = Path(original_name).suffix or ".mp4"

    folder_name = generate_video_folder(original_name)
    raw_filename = f"{folder_name}{ext}"

    raw_path = RAW_VIDEO_DIR / raw_filename
    output_dir = HLS_VIDEO_DIR / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_bytes = await file.read()
    raw_path.write_bytes(raw_bytes)

    # Obtener duración
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(raw_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = float(probe.stdout.strip())
    except:
        duration = 0

    uploaded_at = datetime.utcnow().isoformat()
    playlist_path = output_dir / HLS_PLAYLIST

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(raw_path),
        "-vf", "scale=-2:1080",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "veryfast",
        "-hls_time", "1",
        "-hls_playlist_type", "vod",
        "-progress", "pipe:2",   # <--- progreso por stderr
        "-hls_segment_filename", str(output_dir / "index%d.ts"),
        str(playlist_path),
    ]

    print("[VideoService] Processing: 0%")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        for line in process.stderr:   # <--- ahora stderr
            print_progress(line, duration)

        process.wait()
        print("[VideoService] Processing: 100%")

        metadata = {
            "id": folder_name,
            "originalName": original_name,
            "uploadedAt": uploaded_at,
        }

        (output_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    finally:
        if raw_path.exists():
            os.remove(raw_path)
            print(f"[VideoService] RAW cleaned: {raw_path}")

    return {
        "id": folder_name,
        "originalName": original_name,
        "playlistUrl": f"/streams/{folder_name}/{HLS_PLAYLIST}",
        "uploadedAt": uploaded_at,
    }


async def list_videos() -> list[dict]:
    ensure_upload_folders()
    videos: list[dict] = []

    if not HLS_VIDEO_DIR.exists():
        return videos

    for subdir in HLS_VIDEO_DIR.iterdir():
        metadata_file = subdir / "metadata.json"
        if not metadata_file.exists():
            continue

        data = json.loads(metadata_file.read_text(encoding="utf-8"))
        videos.append({
            "id": data["id"],
            "originalName": data["originalName"],
            "playlistUrl": f"/streams/{subdir.name}/{HLS_PLAYLIST}",
            "uploadedAt": data["uploadedAt"],
        })

    videos.sort(key=lambda v: v["uploadedAt"], reverse=True)
    return videos
