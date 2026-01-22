from pathlib import Path

# Carpeta base del proyecto (donde está main.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Rutas de subida y conversión (igual que en el demo de NestJS)
UPLOAD_ROOT = BASE_DIR / "upload"
RAW_VIDEO_DIR = UPLOAD_ROOT / "raw"
HLS_VIDEO_DIR = UPLOAD_ROOT / "videos"

# Nombre del playlist HLS (igual que HLS_PLAYLIST en TS)
HLS_PLAYLIST = "index.m3u8"


def ensure_upload_folders() -> None:
    """Crea las carpetas necesarias si no existen."""
    for folder in (UPLOAD_ROOT, RAW_VIDEO_DIR, HLS_VIDEO_DIR):
        folder.mkdir(parents=True, exist_ok=True)
