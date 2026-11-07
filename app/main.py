import os
import uuid
import json
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas.layout import (
    VenueLayout,
    GenerateLayoutRequest,
    SaveLayoutRequest
)
from app.services.ai_service import (
    generate_layout_from_ai,
    get_asset_catalog
)

app = FastAPI(
    title="AI Event 3D Layout & Ticketing API",
    description="Backend API untuk merekonstruksi layout acara 3D secara prosedural dari instruksi teks AI.",
    version="1.0.0"
)

# CORS Middleware agar bisa diakses dari frontend mana saja (Next.js, Vue, Mobile, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Direktori penyimpanan layout sederhana (JSON storage)
STORAGE_DIR = Path("data/layouts")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Static files untuk UI 3D Interactive Web
STATIC_DIR = Path("app/static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Menyajikan antarmuka 3D Studio interaktif Three.js langsung di browser."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>3D Studio index.html belum ditemukan</h1>", status_code=404)


@app.get("/api/health")
async def health_check():
    gemini_key_present = bool(os.getenv("GEMINI_API_KEY", "").strip())
    return {
        "status": "online",
        "gemini_configured": gemini_key_present,
        "mode": "AI Gemini Mode" if gemini_key_present else "Smart Fallback Mock Mode"
    }


@app.get("/api/layout/catalog")
async def get_catalog():
    """Mengembalikan katalog aset 3D yang didukung oleh sistem layout."""
    return {"catalog": get_asset_catalog()}


@app.post("/api/layout/generate", response_model=VenueLayout)
async def generate_layout(req: GenerateLayoutRequest):
    """
    Endpoint utama: Menerima instruksi teks pengguna dan mengembalikan
    data terstruktur (JSON) layout 3D ruangan yang siap direkonstruksi oleh frontend.
    """
    try:
        layout = await generate_layout_from_ai(req)
        return layout
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal generate layout: {str(e)}")


@app.post("/api/layout/save")
async def save_layout(req: SaveLayoutRequest):
    """
    Menyimpan hasil modifikasi layout yang sudah digeser/diubah oleh penyaji acara.
    Menghasilkan layout_id untuk dihubungkan ke modul penjualan tiket (seat booking).
    """
    layout_id = req.layout_id or f"layout_{uuid.uuid4().hex[:10]}"
    file_path = STORAGE_DIR / f"{layout_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(req.layout.model_dump(), f, indent=2, ensure_ascii=False)

    # Ekstrak komponen yang bisa dijual tiketnya
    ticketable_items = [item for item in req.layout.items if item.is_bookable]

    return {
        "status": "success",
        "layout_id": layout_id,
        "message": "Layout berhasil disimpan dan siap dihubungkan ke sistem tiket.",
        "summary": {
            "venue_name": req.layout.venue_name,
            "total_capacity": req.layout.total_capacity,
            "ticketable_components_count": len(ticketable_items),
            "tiers": list(set(item.ticket_tier for item in ticketable_items if item.ticket_tier))
        }
    }


@app.get("/api/layout/{layout_id}", response_model=VenueLayout)
async def get_saved_layout(layout_id: str):
    """Mengambil layout tersimpan berdasarkan ID untuk ditampilkan ke pembeli tiket."""
    file_path = STORAGE_DIR / f"{layout_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Layout tidak ditemukan.")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return VenueLayout(**data)

