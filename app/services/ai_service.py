import os
import json
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

from app.schemas.layout import (
    VenueLayout,
    VenueDimensions,
    LayoutItem,
    Position3D,
    Rotation3D,
    Dimensions3D,
    GenerateLayoutRequest
)

load_dotenv()
logger = logging.getLogger(__name__)

# Katalog aset standar 3D yang dikenali sistem
ASSET_CATALOG = [
    {
        "type": "stage",
        "name": "Panggung Utama & LED Screen",
        "description": "Panggung pertunjukan megah dengan layar backdrop LED dan podium",
        "default_dimensions": {"width": 12.0, "height": 4.0, "depth": 4.5},
        "color": "#1e3a8a",
        "is_bookable_default": False
    },
    {
        "type": "table_round",
        "name": "Meja Bundar Banquet Gala Dinner",
        "description": "Meja bundar jamuan resmi lengkap dengan 6-8 kursi banquet melingkar",
        "default_dimensions": {"width": 2.4, "height": 0.85, "depth": 2.4},
        "color": "#f59e0b",
        "is_bookable_default": True,
        "default_capacity": 8
    },
    {
        "type": "chair_row",
        "name": "Blok Kursi Penonton (White Chairs)",
        "description": "Barisan kursi rapi di depan panggung (konferensi/teater)",
        "default_dimensions": {"width": 8.0, "height": 0.85, "depth": 6.0},
        "color": "#ffffff",
        "is_bookable_default": True,
        "default_capacity": 60
    },
    {
        "type": "buffet_station",
        "name": "Meja Prasmanan Catering (Buffet)",
        "description": "Meja jamuan makanan prasmanan dengan pemanas dan hidangan",
        "default_dimensions": {"width": 5.0, "height": 0.9, "depth": 1.5},
        "color": "#b45309",
        "is_bookable_default": False
    },
    {
        "type": "registration_desk",
        "name": "Meja Registrasi & Penerima Tamu",
        "description": "Meja registrasi formal di area foyer pintu masuk",
        "default_dimensions": {"width": 4.0, "height": 1.1, "depth": 1.2},
        "color": "#0369a1",
        "is_bookable_default": False
    },
    {
        "type": "photo_wall",
        "name": "Photo Wall & Red Carpet Backdrop",
        "description": "Backdrop foto resmi dokumentasi dengan karpet merah",
        "default_dimensions": {"width": 4.5, "height": 2.8, "depth": 2.0},
        "color": "#be123c",
        "is_bookable_default": False
    },
    {
        "type": "tent_sarnafil",
        "name": "Tenda Kerucut Sarnafil (Khusus Outdoor)",
        "description": "Tenda acara atap kerucut putih (hanya untuk acara outdoor)",
        "default_dimensions": {"width": 4.0, "height": 3.8, "depth": 4.0},
        "color": "#0284c7",
        "is_bookable_default": True,
        "default_capacity": 10
    },
    {
        "type": "booth_expo",
        "name": "Stan Pameran / Sponsor",
        "description": "Booth pameran dengan kanopi rangka dan meja kasir",
        "default_dimensions": {"width": 3.0, "height": 2.6, "depth": 3.0},
        "color": "#ec4899",
        "is_bookable_default": False
    },
    {
        "type": "speaker_tower",
        "name": "Sound System Tower",
        "description": "Menara audio kiri/kanan panggung",
        "default_dimensions": {"width": 1.2, "height": 3.5, "depth": 1.2},
        "color": "#0f172a",
        "is_bookable_default": False
    },
    {
        "type": "gate_entrance",
        "name": "Pintu Masuk Utama (Ballroom Entrance)",
        "description": "Pintu masuk ganda dan akses tamu ke dalam ruangan",
        "default_dimensions": {"width": 5.0, "height": 3.5, "depth": 1.0},
        "color": "#06b6d4",
        "is_bookable_default": False
    }
]


def get_asset_catalog() -> List[Dict[str, Any]]:
    return ASSET_CATALOG


def generate_fallback_layout(req: GenerateLayoutRequest) -> VenueLayout:
    w = req.venue_width or 34.0
    l = req.venue_length or 26.0
    prompt_lower = req.prompt.lower()

    is_gala = any(k in prompt_lower for k in ["gala", "dinner", "jamuan", "makan malam", "meja bundar"])
    is_indoor = not any(k in prompt_lower for k in ["outdoor", "lapangan", "taman", "festival outdoor"]) or is_gala

    items: List[LayoutItem] = []

    if is_gala or is_indoor:
        # --- LAYOUT INDOOR GRAND BALLROOM GALA DINNER ---
        stage_z = -(l / 2) + 3.5
        items.append(
            LayoutItem(
                id="stage-main",
                type="stage",
                name="Panggung Utama & LED Grand Screen",
                position=Position3D(x=0.0, y=0.0, z=stage_z),
                dimensions=Dimensions3D(width=min(14.0, w * 0.55), height=4.0, depth=4.5),
                color="#1e1b4b",
                is_locked=True
            )
        )

        items.append(
            LayoutItem(
                id="speaker-left",
                type="speaker_tower",
                name="Sound System Kiri",
                position=Position3D(x=-8.5, y=0.0, z=stage_z + 0.5),
                dimensions=Dimensions3D(width=1.2, height=3.5, depth=1.2),
                color="#0f172a"
            )
        )
        items.append(
            LayoutItem(
                id="speaker-right",
                type="speaker_tower",
                name="Sound System Kanan",
                position=Position3D(x=8.5, y=0.0, z=stage_z + 0.5),
                dimensions=Dimensions3D(width=1.2, height=3.5, depth=1.2),
                color="#0f172a"
            )
        )

        # Meja-meja Bundar Banquet VIP (Depan panggung)
        vip_z = stage_z + 5.5
        for col_i, x_pos in enumerate([-5.5, 0.0, 5.5]):
            items.append(
                LayoutItem(
                    id=f"table-vip-0{col_i+1}",
                    type="table_round",
                    name=f"Meja VVIP #{col_i+1}",
                    position=Position3D(x=x_pos, y=0.0, z=vip_z),
                    dimensions=Dimensions3D(width=2.6, height=0.85, depth=2.6),
                    color="#f59e0b",
                    is_bookable=True,
                    ticket_tier="VVIP Banquet",
                    capacity=8,
                    price_estimate=1500000.0
                )
            )

        # Meja-meja Bundar Banquet Reguler (Tengah ballroom)
        row_z_list = [vip_z + 4.5, vip_z + 9.0]
        table_num = 1
        for r_z in row_z_list:
            for x_pos in [-8.0, -2.7, 2.7, 8.0]:
                tier = "VIP Dining" if r_z < vip_z + 7.0 else "Regular Dining"
                items.append(
                    LayoutItem(
                        id=f"table-banquet-{table_num}",
                        type="table_round",
                        name=f"Meja Jamuan #{table_num}",
                        position=Position3D(x=x_pos, y=0.0, z=r_z),
                        dimensions=Dimensions3D(width=2.4, height=0.85, depth=2.4),
                        color="#d97706",
                        is_bookable=True,
                        ticket_tier=tier,
                        capacity=8,
                        price_estimate=950000.0 if "VIP" in tier else 650000.0
                    )
                )
                table_num += 1

        # Meja Prasmanan Catering (Buffet Stations di sisi kiri dan kanan)
        items.append(
            LayoutItem(
                id="buffet-left",
                type="buffet_station",
                name="Prasmanan Katering Utama (Kiri)",
                position=Position3D(x=-(w / 2) + 3.0, y=0.0, z=0.0),
                rotation=Rotation3D(y=90.0),
                dimensions=Dimensions3D(width=6.0, height=0.9, depth=1.6),
                color="#b45309"
            )
        )
        items.append(
            LayoutItem(
                id="buffet-right",
                type="buffet_station",
                name="Dessert & Beverage Bar (Kanan)",
                position=Position3D(x=(w / 2) - 3.0, y=0.0, z=0.0),
                rotation=Rotation3D(y=-90.0),
                dimensions=Dimensions3D(width=6.0, height=0.9, depth=1.6),
                color="#b45309"
            )
        )

        # Photo Wall & Red Carpet di area foyer depan kiri
        entrance_z = (l / 2) - 3.0
        items.append(
            LayoutItem(
                id="photo-wall-main",
                type="photo_wall",
                name="Photo Wall & Red Carpet Session",
                position=Position3D(x=-6.5, y=0.0, z=entrance_z),
                rotation=Rotation3D(y=0.0),
                dimensions=Dimensions3D(width=4.5, height=2.8, depth=2.0),
                color="#be123c"
            )
        )

        # Meja Registrasi di depan kanan
        items.append(
            LayoutItem(
                id="reg-desk",
                type="registration_desk",
                name="Meja Registrasi & Guestbook",
                position=Position3D(x=6.5, y=0.0, z=entrance_z),
                rotation=Rotation3D(y=0.0),
                dimensions=Dimensions3D(width=4.0, height=1.1, depth=1.2),
                color="#0369a1"
            )
        )

        # Pintu Masuk Utama Ballroom
        items.append(
            LayoutItem(
                id="gate-entry",
                type="gate_entrance",
                name="Pintu Masuk Utama Grand Ballroom",
                position=Position3D(x=0.0, y=0.0, z=(l / 2) - 1.2),
                dimensions=Dimensions3D(width=5.0, height=3.5, depth=1.0),
                color="#06b6d4"
            )
        )

        env = "indoor"
        desc = "Tata letak resmi Indoor Grand Ballroom Gala Dinner: panggung utama megah berlayar LED, meja banquet bundar VIP & reguler dengan kursi melingkar rapi, dua buffet station katering, photo wall red carpet, dan meja registrasi foyer."

    else:
        # Outdoor festival fallback
        env = "outdoor"
        stage_z = -(l / 2) + 3.5
        items.append(
            LayoutItem(
                id="stage-main",
                type="stage",
                name="Panggung Utama Festival",
                position=Position3D(x=0.0, y=0.0, z=stage_z),
                dimensions=Dimensions3D(width=12.0, height=4.2, depth=4.5),
                color="#1e3a8a",
                is_locked=True
            )
        )
        desc = "Tata letak festival outdoor terbuka."

    total_cap = sum(item.capacity for item in items if item.is_bookable)

    return VenueLayout(
        venue_name=req.venue_name or ("Grand Ballroom Hotel" if is_indoor else "Festival Grounds"),
        environment_type=env,
        dimensions=VenueDimensions(width=w, length=l, height=6.0),
        description=desc,
        total_capacity=total_cap,
        items=items
    )


async def generate_layout_from_ai(req: GenerateLayoutRequest) -> VenueLayout:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        logger.warning("GEMINI_API_KEY belum disetel di .env. Menggunakan Fallback Generator.")
        return generate_fallback_layout(req)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        w = req.venue_width or 34.0
        l = req.venue_length or 26.0

        system_prompt = f"""
Anda adalah Senior Professional Venue Space Planner & Arsitek Tata Ruang Event (Gala Dinner, Ballroom, Konferensi, Expo).
Tugas Anda adalah merancang tata letak spasial 3D yang presisi, proporsional, mewah, dan berkelas.

KLASIFIKASI LINGKUNGAN (environment_type):
- Set environment_type = "indoor" jika acara bertema Gala Dinner, Ballroom, Jamuan Makan, Pernikahan, Konferensi Hotel, Gedung Pertemuan.
  * PENTING: Untuk acara indoor/ballroom, DILARANG KERAS menggunakan tenda kerucut (tent_sarnafil) atau booth bazar jalanan!
  * Komponen Indoor Resmi:
    - 'table_round': Meja bundar banquet lengkap dengan kursi gala dinner (is_bookable: true, kapasitas: 8, tier: VIP/Regular Dining).
    - 'stage': Panggung utama indoor dengan layar backdrop LED megah & podium pidato di Z negatif.
    - 'buffet_station': Meja prasmanan katering panjang untuk penyajian makanan & minuman di sisi samping/belakang.
    - 'registration_desk': Meja registrasi & penerima tamu di dekat pintu masuk.
    - 'photo_wall': Backdrop sesi foto dokumentasi & red carpet.
    - 'gate_entrance': Pintu masuk utama ballroom di sisi Z positif.
    - 'speaker_tower': Menara audio sound system di kiri & kanan panggung.
- Set environment_type = "outdoor" HANYA jika pengguna secara spesifik meminta festival lapangan terbuka atau bazar outdoor.

KOORDINAT VENUE:
- Lebar (sumbu X): rentang -{w/2:.1f} m (kiri) sampai +{w/2:.1f} m (kanan).
- Panjang (sumbu Z): rentang -{l/2:.1f} m (belakang/area panggung) sampai +{l/2:.1f} m (depan/pintu masuk).
- Lantai berada di Y = 0.
- SEMUA OBJEK WAJIB MENAPAK DI LANTAI dengan position.y = 0.0 (DILARANG melayang di udara).

ATURAN WAJIB TATA RUANG GALA DINNER:
1. Panggung megah berada di sisi belakang (Z negatif).
2. Meja bundar banquet diletakkan rapi dan simetris di tengah ruangan, dibagi menjadi Meja VIP/VVIP (di baris depan terdekat dengan panggung) dan Meja Reguler di belakangnya.
3. Seluruh meja tamu harus memiliki jarak sirkulasi jalan aman minimal 2-2.5 meter untuk mobilitas waiter katering dan tamu.
4. Meja prasmanan (buffet_station) diletakkan di sisi dinding samping atau belakang agar distribusi katering lancar tanpa memotong pandangan ke panggung.
5. Meja registrasi dan Photo Wall ditempatkan dekat pintu masuk (Z positif) untuk alur penyambutan tamu (guest flow).
6. Komponen tiket (meja banquet) WAJIB diisi: is_bookable: true, tier yang jelas (VVIP, VIP, Regular Dining), kapasitas 8 orang/meja, dan estimasi harga per meja/kursi.
"""

        user_content = f"""
Permintaan Acara: {req.prompt}
Nama Gedung/Venue: {req.venue_name}
Ukuran Ruangan: Lebar {w} meter, Panjang {l} meter
Tipe Acara: {req.event_type}

Rancang tata letak lengkap profesional sesuai kebutuhan acara tersebut.
"""

        models_to_try = [
            #"gemini-3.5-flash",
            #"gemini-3.5-flash-lite",
            #"gemini-3.7-flash",
            #"gemini-3.8-flash",
            #"gemini-flash-latest"
            "claude-sonnet-4-6"
        ]

        response = None
        last_error = None

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        response_schema=VenueLayout,
                        temperature=0.3
                    )
                )
                if response and response.text:
                    logger.info(f"Berhasil menggunakan model: {model_name}")
                    break
            except Exception as model_err:
                logger.warning(f"Percobaan model {model_name} gagal: {model_err}")
                last_error = model_err

        if not response or not response.text:
            raise last_error or Exception("Tidak ada respons dari Gemini API.")

        layout_dict = json.loads(response.text)
        layout = VenueLayout(**layout_dict)

        # Force clamp y to 0.0 for safety
        for item in layout.items:
            item.position.y = 0.0

        calculated_cap = sum(item.capacity for item in layout.items if item.is_bookable)
        if layout.total_capacity == 0 or layout.total_capacity is None:
            layout.total_capacity = calculated_cap

        return layout

    except Exception as e:
        logger.error(f"Gagal memanggil Gemini API: {e}. Mengalihkan ke fallback generator.")
        return generate_fallback_layout(req)
