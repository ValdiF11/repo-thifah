# 🎪 AI 3D Event Layout Studio & Ticketing System

Sistem pembuatan rekomendasi tata letak acara (layout 3D) berbasis AI yang **dapat direkonstruksi dan diedit secara interaktif** (bukan sekadar gambar statis).

Hasil rekomendasi AI berbentuk **Scene Graph (Data Terstruktur JSON)** yang memetakan posisi spasial 3D setiap panggung, meja VIP, deretan kursi, area festival, booth makanan, dan gerbang tiket.

---

## 🌟 Fitur Utama

1. **AI Spasial Scene Generator**:
   - Menerjemahkan kebutuhan acara (teks bebas) menjadi data koordinat spasial 3D `(X, Y, Z)`.
   - Menghasilkan kapasitas kuota, kategori tiket (VIP, Regular, Festival), dan estimasi harga secara otomatis.
   - Menggunakan Gemini API Structured Outputs (`gemini-2.5-flash`), dengan mode *Smart Fallback Generator* jika dijalankan secara offline atau tanpa API key.

2. **Interactive 3D Editor (Three.js)**:
   - **Bukan Gambar Mati**: Seluruh ruangan dapat dijelajahi dengan kamera orbit (putar, zoom, geser).
   - **Drag & Drop (Gizmo)**: Klik objek (misal: meja atau panggung) lalu geser atau putar posisinya secara langsung.
   - **Inspector Panel**: Ubah nama, kapasitas, dan tier tiket langsung di layar.

3. **Ticketing Integration**:
   - Komponen dengan status `is_bookable: true` langsung terhubung dengan kuota dan kategori tiket.
   - Tombol **Simpan Layout** menyimpan koordinat akhir ke database/JSON untuk digunakan oleh modul pembelian tiket pengunjung (*seat selection*).

---

## 🚀 Cara Menjalankan Proyek

### 1. Masuk ke Virtual Environment
Di terminal PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. (Opsional) Masukkan API Key Gemini
Buka file [`.env`](file:///d:/LATHIFAH%20HUSNUN/Work/urbansolv-maganghub/Hackaton/.env) dan masukkan API Key Anda:
```env
GEMINI_API_KEY=AIzaSy...
```
*(Catatan: Jika dikosongkan, sistem otomatis mengaktifkan Smart Fallback Generator sehingga demo tetap berjalan lancar).*

### 3. Jalankan Aplikasi
```powershell
python run.py
```
atau menggunakan uvicorn langsung:
```powershell
uvicorn app.main:app --reload
```

Buka browser Anda di:
* **Interactive 3D Studio**: [http://localhost:8000](http://localhost:8000)
* **Dokumentasi API Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Menjalankan Pengujian (Unit Tests)

```powershell
python -m pytest tests/
```

---

## 📡 Dokumentasi Endpoint API

| Method | Endpoint | Keterangan |
| :--- | :--- | :--- |
| `GET` | `/` | Antarmuka web 3D editor interaktif |
| `POST` | `/api/layout/generate` | Generate layout 3D dari teks prompt AI |
| `POST` | `/api/layout/save` | Simpan layout yang sudah digeser/diedit oleh user |
| `GET` | `/api/layout/{layout_id}` | Ambil layout tersimpan berdasarkan ID |
| `GET` | `/api/layout/catalog` | Daftar katalog komponen 3D yang didukung |
| `GET` | `/api/health` | Status server dan konfigurasi AI |

