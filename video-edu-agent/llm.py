import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

# --- Gemini 2.5 Flash (Primary) — SDK terbaru google-genai ---
from google import genai as _genai
from google.genai import types as _types

GEMINI_MODEL = "gemini-2.5-flash"

# --- Clients ---
_gemini_client = None
_groq_client = None

def _get_gemini():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = _genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _gemini_client

def _get_groq():
    global _groq_client
    if _groq_client is None:
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and groq_key != "isi_groq_api_key_di_sini":
            from groq import Groq
            _groq_client = Groq(api_key=groq_key)
    return _groq_client


PROMPT_TEMPLATE = """
Kamu adalah pembuat konten edukasi profesional. Buat script video edukasi berkualitas tinggi.

Topik    : {topic}
Audience : {audience}
Durasi   : {duration_sec} detik
Bahasa   : {language_name}

Buat 4-5 scene yang menarik dan informatif. Setiap scene harus memiliki:
- Narasi yang mengalir natural dan mudah dipahami
- Subtitle singkat dan jelas (maks 10 kata per baris)
- Deskripsi visual spesifik dan vivid untuk AI image generator (dalam Bahasa Inggris)

Balas HANYA dengan JSON valid berikut ini, tanpa penjelasan atau markdown apapun:
[
  {{
    "scene_id": 1,
    "narration": "teks yang dibacakan narrator, minimal 2 kalimat",
    "subtitle": "teks subtitle singkat",
    "visual": "detailed visual description for AI image generator in English",
    "duration_sec": 12
  }}
]
"""


def _parse_json(text: str) -> list:
    """Bersihkan dan parse JSON dari respons LLM."""
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("["):
                text = part
                break
    # Cari array JSON di dalam teks
    start = text.find("[")
    end   = text.rfind("]")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text.strip())


def generate_scenes(topic: str, audience: str, duration_sec: int, language: str) -> list:
    """
    Generate scene script via LLM.
    Primary  : Gemini 2.5 Flash (google-genai SDK terbaru)
    Fallback : Groq — llama-3.3-70b-versatile
    """
    language_name = "Indonesia" if language == "id" else "English"
    prompt = PROMPT_TEMPLATE.format(
        topic=topic,
        audience=audience,
        duration_sec=duration_sec,
        language_name=language_name,
    )

    # --- 1. Gemini 2.5 Flash (Primary) ---
    try:
        print(f"[LLM] Menggunakan {GEMINI_MODEL} (primary)...")
        client = _get_gemini()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=_types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=2048,
            ),
        )
        scenes = _parse_json(response.text)
        print(f"[LLM] ✓ Gemini berhasil menghasilkan {len(scenes)} scene.")
        return scenes
    except Exception as e:
        print(f"[LLM] Gemini gagal ({e}), beralih ke Groq fallback...")

    # --- 2. Groq Llama 3.3 70B (Fallback) ---
    groq = _get_groq()
    if groq is None:
        raise RuntimeError(
            "Gemini gagal dan GROQ_API_KEY tidak dikonfigurasi. "
            "Isi GROQ_API_KEY di .env — daftar gratis di https://console.groq.com"
        )

    try:
        print("[LLM] Menggunakan Groq llama-3.3-70b-versatile (fallback)...")
        completion = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah pembuat konten edukasi profesional. "
                        "Selalu balas hanya dengan JSON valid tanpa penjelasan apapun."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        text   = completion.choices[0].message.content
        scenes = _parse_json(text)
        print(f"[LLM] ✓ Groq berhasil menghasilkan {len(scenes)} scene.")
        return scenes
    except Exception as e:
        raise RuntimeError(f"Semua LLM gagal. Error Groq terakhir: {e}")
