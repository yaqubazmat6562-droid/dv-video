import os
import uuid
import shutil
import subprocess
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------- Setup ----------
UPLOAD_DIR = Path("web_uploads")
OUTPUT_DIR = Path("web_outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="DV Studio Mobile")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (uploads / outputs)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")
# Static folder for web UI
app.mount("/static", StaticFiles(directory="web_ui"), name="static")

# ---------- Models ----------
class TrimRequest(BaseModel):
    file_id: str
    start: float
    end: float

class SpeedRequest(BaseModel):
    file_id: str
    speed: float

class FilterRequest(BaseModel):
    file_id: str
    preset: str
    brightness: float = 0.0
    contrast: float = 1.0
    saturation: float = 1.0

class TextRequest(BaseModel):
    file_id: str
    text: str
    position: str = "bottom"
    color: str = "white"
    font_size: int = 48

# ---------- Helper ----------
def _get_input(file_id: str) -> Path:
    """file_id سے اصل پاتھ نکالیں"""
    for f in UPLOAD_DIR.iterdir():
        if f.stem == file_id:
            return f
    raise HTTPException(404, "File not found")

def _run_ffmpeg(cmd):
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="ignore"
    )
    if result.returncode != 0:
        raise HTTPException(500, f"FFmpeg error: {result.stderr[-300:]}")
    return result

# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
async def index():
    """مین پیج"""
    html_path = Path("web_ui/index.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return "<h1>DV Studio Mobile</h1><p>UI not found</p>"

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    """ویڈیو اپلوڈ کریں"""
    file_id = str(uuid.uuid4())[:8]
    ext = Path(file.filename).suffix
    save_path = UPLOAD_DIR / f"{file_id}{ext}"

    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Duration معلوم کریں
    try:
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(save_path)
        ], capture_output=True, text=True)
        import json
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
    except Exception:
        duration = 0.0

    return {
        "file_id": file_id,
        "filename": file.filename,
        "url": f"/uploads/{file_id}{ext}",
        "duration": duration,
    }

@app.post("/api/trim")
async def trim(req: TrimRequest):
    """ویڈیو کاٹیں"""
    src = _get_input(req.file_id)
    out_id = f"{req.file_id}_trim_{uuid.uuid4().hex[:4]}"
    out_path = OUTPUT_DIR / f"{out_id}.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-ss", str(req.start),
        "-to", str(req.end),
        "-c", "copy",
        str(out_path)
    ]
    _run_ffmpeg(cmd)

    return {
        "output_id": out_id,
        "url": f"/outputs/{out_id}.mp4"
    }

@app.post("/api/speed")
async def speed(req: SpeedRequest):
    """رفتار تبدیل کریں"""
    src = _get_input(req.file_id)
    out_id = f"{req.file_id}_speed_{uuid.uuid4().hex[:4]}"
    out_path = OUTPUT_DIR / f"{out_id}.mp4"

    speed = max(0.25, min(4.0, req.speed))
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-filter_complex",
        f"[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]",
        "-map", "[v]", "-map", "[a]",
        str(out_path)
    ]
    _run_ffmpeg(cmd)

    return {"output_id": out_id, "url": f"/outputs/{out_id}.mp4"}

@app.post("/api/filter")
async def apply_filter(req: FilterRequest):
    """فلٹر لگائیں"""
    from core.filters import VideoFilters
    src = _get_input(req.file_id)
    out_id = f"{req.file_id}_filter_{uuid.uuid4().hex[:4]}"
    out_path = OUTPUT_DIR / f"{out_id}.mp4"

    ok, msg = VideoFilters.apply_filter(
        str(src), str(out_path),
        preset=req.preset,
        brightness=req.brightness,
        contrast=req.contrast,
        saturation=req.saturation,
    )
    if not ok:
        raise HTTPException(500, msg)

    return {"output_id": out_id, "url": f"/outputs/{out_id}.mp4"}

@app.post("/api/text")
async def add_text(req: TextRequest):
    """ٹیکسٹ لگائیں"""
    from core.text_overlay import TextOverlay
    src = _get_input(req.file_id)
    out_id = f"{req.file_id}_text_{uuid.uuid4().hex[:4]}"
    out_path = OUTPUT_DIR / f"{out_id}.mp4"

    pos_map = {
        "top": "اوپر",
        "middle": "درمیان",
        "bottom": "نیچے",
    }
    color_map = {
        "white": "سفید",
        "black": "کالا",
        "red": "سرخ",
        "yellow": "پیلا",
        "blue": "نیلا",
    }

    ok, msg = TextOverlay.add_text(
        str(src), str(out_path),
        text=req.text,
        position=pos_map.get(req.position, "نیچے"),
        color=color_map.get(req.color, "سفید"),
        font_size=req.font_size,
    )
    if not ok:
        raise HTTPException(500, msg)

    return {"output_id": out_id, "url": f"/outputs/{out_id}.mp4"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "DV Studio Mobile چل رہا ہے!"}


if __name__ == "__main__":
    import uvicorn
    print("🚀 DV Studio Mobile Server")
    print("📱 موبائل سے کھولیں: http://<your-pc-ip>:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)