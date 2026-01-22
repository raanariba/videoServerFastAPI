import os
from pathlib import Path


def _load_dotenv() -> None:
    """
    Carga variables desde .env si existen y no est??n definidas en el proceso.
    """
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

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
