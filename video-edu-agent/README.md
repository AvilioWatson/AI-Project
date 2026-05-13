# 🎬 Video Edu Agent

> Generate educational videos automatically using AI — **100% Free** ($0)

## Tech Stack

| Komponen   | Tool                          | Biaya |
|------------|-------------------------------|-------|
| Backend    | FastAPI + Python              | $0    |
| Database   | SQLite                        | $0    |
| LLM        | Google Gemini API (free tier) | $0    |
| TTS/Suara  | edge-tts (Microsoft)          | $0    |
| Gambar     | Pillow                        | $0    |
| Video      | MoviePy                       | $0    |
| **TOTAL**  |                               | **$0**|

---

## Cara Setup

### 1. Clone & buat virtual environment

```bash
cd video-edu-agent
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Buat file `.env`

```bash
copy .env.example .env
```

Edit `.env` dan isi API key kamu:
```
GEMINI_API_KEY=isi_api_key_kamu_di_sini
```

> Dapatkan API key gratis di [aistudio.google.com](https://aistudio.google.com) → **Get API Key**

### 4. Jalankan server

```bash
uvicorn main:app --reload
```

Buka browser: **http://localhost:8000/docs**

---

## API Endpoints

| Method | Endpoint                 | Fungsi                      |
|--------|--------------------------|-----------------------------|
| POST   | `/create-video`          | Buat video baru (async)     |
| GET    | `/status/{project_id}`   | Cek status project          |
| GET    | `/download/{project_id}` | Download video final (.mp4) |
| GET    | `/projects`              | List semua project          |
| GET    | `/docs`                  | Swagger UI                  |

---

## Contoh Penggunaan

### Buat video baru

```bash
curl -X POST http://localhost:8000/create-video \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "apa itu inflasi",
    "audience": "pelajar SMA",
    "duration_sec": 60,
    "language": "id"
  }'
```

**Response:**
```json
{
  "project_id": "a1b2c3d4",
  "status": "planning",
  "message": "Video sedang diproses. Cek status di /status/a1b2c3d4",
  "status_url": "/status/a1b2c3d4",
  "download": "/download/a1b2c3d4"
}
```

### Cek status

```bash
curl http://localhost:8000/status/a1b2c3d4
```

### Download video

```bash
http://localhost:8000/download/a1b2c3d4
```

---

## Status Lifecycle

| Status      | Artinya                               |
|-------------|---------------------------------------|
| `draft`     | Project baru dibuat                   |
| `planning`  | Gemini sedang generate script         |
| `rendering` | Audio + slide + video sedang diproses |
| `completed` | Video siap diunduh ✅                 |
| `failed`    | Ada error — cek field `error`         |

---

## Struktur Folder

```
video-edu-agent/
├── main.py        ← FastAPI app (semua endpoint)
├── database.py    ← SQLite setup
├── llm.py         ← Panggil Gemini
├── tts.py         ← Generate audio per scene
├── slide.py       ← Buat gambar slide per scene
├── video.py       ← Render & gabungkan video
├── subtitle.py    ← Generate file .srt
├── requirements.txt
├── .env.example   ← Template env (salin ke .env)
├── .env           ← API key (JANGAN di-commit!)
└── outputs/       ← Hasil video tersimpan di sini
    └── {project_id}/
        ├── audio/
        │   ├── scene_1.mp3
        │   └── scene_2.mp3
        ├── slides/
        │   ├── scene_1.png
        │   └── scene_2.png
        ├── subtitle.srt
        └── final.mp4
```
