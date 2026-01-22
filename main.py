from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from fastapi.middleware.cors import CORSMiddleware

from app.api.video_api import router as video_router


# ===============================
# Paths & Templates
# ===============================
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
INDEX_FILE = TEMPLATES_DIR / "index.html"


# ===============================
# FastAPI App
# ===============================
app = FastAPI(
    title="Python Video Server",
    version="1.0.0",
    description="Video Processing API (FFmpeg/HLS)",
    docs_url=None,       # Deshabilitamos docs default
    redoc_url=None,
    openapi_url="/openapi.json",
)


# ===============================
# UI Home (HLS Converter)
# ===============================
@app.get("/", include_in_schema=False)
def home():
    """
    Página principal con UI del conversor HLS.
    """
    if not INDEX_FILE.exists():
        return HTMLResponse(
            "<h1>Templates not found</h1><p>Missing templates/index.html</p>",
            status_code=500,
        )

    html = INDEX_FILE.read_text(encoding="utf-8")
    return HTMLResponse(content=html, media_type="text/html")


# ===============================
# Swagger Custom
# ===============================
@app.get("/swagger", include_in_schema=False)
def swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Video Server Swagger",
    )


# ===============================
# API Routes
# ===============================
app.include_router(video_router, prefix="/videos")


# ===============================
# Static HLS Streaming
# ===============================
# Sirve:
#   /streams/<videoId>/index.m3u8
#   /streams/<videoId>/index.ts
#   etc.
app.mount(
    "/streams",
    StaticFiles(directory="upload/videos"),
    name="streams",
)


# ===============================
# (Opcional) CORS for frontend
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # puedes restringir si lo usas en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
