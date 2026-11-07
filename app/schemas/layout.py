from typing import List, Optional
from pydantic import BaseModel, Field


class Position3D(BaseModel):
    x: float = Field(..., description="Posisi horizontal X (kiri/kanan) dalam meter")
    y: float = Field(default=0.0, description="Posisi vertikal Y (tinggi/lantai) dalam meter. 0 = lantai")
    z: float = Field(..., description="Posisi kedalaman Z (depan/belakang) dalam meter")


class Rotation3D(BaseModel):
    x: float = Field(default=0.0, description="Rotasi sumbu X dalam derajat")
    y: float = Field(default=0.0, description="Rotasi sumbu Y dalam derajat (hadap panggung/audiens)")
    z: float = Field(default=0.0, description="Rotasi sumbu Z dalam derajat")


class Dimensions3D(BaseModel):
    width: float = Field(..., description="Lebar objek (sumbu X) dalam meter")
    height: float = Field(..., description="Tinggi objek (sumbu Y) dalam meter")
    depth: float = Field(..., description="Kedalaman objek (sumbu Z) dalam meter")


class LayoutItem(BaseModel):
    id: str = Field(..., description="ID unik komponen (contoh: stage-01, vip-table-01)")
    type: str = Field(
        ...,
        description="Tipe katalog aset: stage, table_round, chair_row, booth_expo, booth_fnb, speaker_tower, gate_entrance, standing_area"
    )
    name: str = Field(..., description="Nama komponen yang mudah dibaca (contoh: Panggung Utama, Meja VIP 1)")
    position: Position3D = Field(..., description="Koordinat posisi di ruangan")
    rotation: Rotation3D = Field(default_factory=Rotation3D, description="Rotasi objek dalam derajat")
    dimensions: Dimensions3D = Field(..., description="Dimensi fisik objek")
    color: Optional[str] = Field(default="#64748b", description="Kode warna heksadesimal (contoh: #eab308, #3b82f6)")
    is_bookable: bool = Field(default=False, description="Apakah komponen ini bisa dibeli tiketnya oleh pengunjung?")
    ticket_tier: Optional[str] = Field(default=None, description="Kategori tiket (contoh: VVIP, VIP, Festival, Reguler)")
    capacity: int = Field(default=0, description="Kapasitas kuota orang/kursi pada komponen ini")
    price_estimate: Optional[float] = Field(default=0.0, description="Rekomendasi harga tiket satuan dalam IDR")
    is_locked: bool = Field(default=False, description="Jika true, komponen tidak boleh digeser secara bebas")


class VenueDimensions(BaseModel):
    width: float = Field(default=30.0, description="Lebar ruangan dalam meter")
    length: float = Field(default=20.0, description="Panjang ruangan dalam meter")
    height: float = Field(default=6.0, description="Tinggi plafon ruangan dalam meter")
    unit: str = Field(default="meters", description="Satuan ukuran")


class VenueLayout(BaseModel):
    venue_name: str = Field(default="Main Hall", description="Nama venue/ruangan acara")
    environment_type: Optional[str] = Field(default="indoor", description="Tipe lingkungan: 'indoor' (ballroom/gedung) atau 'outdoor' (lapangan/taman)")
    dimensions: VenueDimensions = Field(default_factory=VenueDimensions)
    description: Optional[str] = Field(default="", description="Penjelasan konsep tata letak dari AI")
    total_capacity: int = Field(default=0, description="Total kapasitas pengunjung yang dapat ditampung")
    items: List[LayoutItem] = Field(default_factory=list, description="Daftar seluruh komponen di dalam ruangan")


class GenerateLayoutRequest(BaseModel):
    prompt: str = Field(..., description="Instruksi/kebutuhan acara dari penyaji acara")
    venue_name: Optional[str] = Field(default="Main Hall", description="Nama gedung/ruangan")
    venue_width: Optional[float] = Field(default=30.0, description="Lebar ruangan (meter)")
    venue_length: Optional[float] = Field(default=20.0, description="Panjang ruangan (meter)")
    event_type: Optional[str] = Field(default="general", description="Tipe acara: concert, exhibition, seminar, wedding, etc.")
    environment_type: Optional[str] = Field(default=None, description="'indoor' atau 'outdoor'")


class SaveLayoutRequest(BaseModel):
    layout_id: Optional[str] = Field(default=None, description="ID layout jika sudah pernah disimpan")
    layout: VenueLayout

