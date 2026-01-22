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
            print(f"[VideoService][GPU] Processing: {pct:.0f}%")
        except:
            pass


def is_gpu_available() -> bool:
    """
    Verifica si FFmpeg tiene el encoder NVENC disponible.
    """
    try:
        probe = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output = f"{probe.stdout}\n{probe.stderr}"
        return "h264_nvenc" in output
    except:
        return False


def get_gpu_info() -> str | None:
    """
    Intenta obtener info bÃ¡sica del dispositivo via nvidia-smi.
    """
    try:
        probe = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        info = probe.stdout.strip()
        if info:
            return info
    except:
        pass

    try:
        probe = subprocess.run(
            ["nvidia-smi", "-L"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        info = probe.stdout.strip()
        if info:
            return info
    except:
        pass

    return None


async def convert_to_hls(file: UploadFile) -> dict:
    ensure_upload_folders()

    if not file.filename:
        raise HTTPException(status_code=400, detail="Archivo invÃ¡lido")

    gpu_info = get_gpu_info()
    if gpu_info:
        print(f"[VideoService][GPU] Using GPU: {gpu_info}")
    else:
        print("[VideoService][GPU] Using GPU (device info unavailable)")

    original_name = file.filename
    ext = Path(original_name).suffix or ".mp4"

    folder_name = generate_video_folder(original_name)
    raw_filename = f"{folder_name}{ext}"

    raw_path = RAW_VIDEO_DIR / raw_filename
    output_dir = HLS_VIDEO_DIR / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_bytes = await file.read()
    raw_path.write_bytes(raw_bytes)

    # Obtener duraciÃ³n
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
        "-c:v", "copy",
        "-c:a", "copy",
        "-hls_time", "1",
        "-hls_playlist_type", "vod",
        "-progress", "pipe:2",   # <--- progreso por stderr
        "-hls_segment_filename", str(output_dir / "index%d.ts"),
        str(playlist_path),
    ]

    print("[VideoService][GPU] Processing: 0%")

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
        print("[VideoService][GPU] Processing: 100%")

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
            print(f"[VideoService][GPU] RAW cleaned: {raw_path}")

    return {
        "id": folder_name,
        "originalName": original_name,
        "playlistUrl": f"/streams/{folder_name}/{HLS_PLAYLIST}",
        "uploadedAt": uploaded_at,
    }
