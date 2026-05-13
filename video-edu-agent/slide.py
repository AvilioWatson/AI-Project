from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import time
from dotenv import load_dotenv

load_dotenv()


def create_slide(visual_desc: str, slide_number: int, output_path: str):
    W, H = 720, 1280  # 9:16 untuk mobile / short video

    # --- 1. Generate gambar via Hugging Face (FLUX.1-schnell) ---
    hf_token = os.getenv("HF_TOKEN")

    if hf_token:
        # Prompt engineering optimal untuk FLUX.1-schnell (gaya edukasi)
        flux_prompt = (
            f"{visual_desc}, "
            "educational illustration, vibrant colors, clean flat design, "
            "highly detailed, professional infographic style, "
            "bright background, no text overlays"
        )

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                from huggingface_hub import InferenceClient

                print(
                    f"[Slide] Generating AI image scene {slide_number} "
                    f"via FLUX.1-schnell (attempt {attempt}/{max_retries})..."
                )
                client = InferenceClient(
                    "black-forest-labs/FLUX.1-schnell",
                    token=hf_token,
                )

                # FLUX.1-schnell optimal di 4 steps
                image = client.text_to_image(
                    flux_prompt,
                    width=768,
                    height=1280,
                    num_inference_steps=4,
                )

                # Resize ke dimensi target
                image = image.resize((W, H), Image.LANCZOS)
                image.save(output_path)
                print(f"[Slide] ✓ AI image scene {slide_number} berhasil dibuat.")
                return

            except Exception as e:
                err_str = str(e).lower()
                if "rate" in err_str or "429" in err_str or "too many" in err_str:
                    wait = attempt * 15  # 15s, 30s, 45s
                    print(
                        f"[Slide] Rate limit HF scene {slide_number}, "
                        f"tunggu {wait}s lalu retry..."
                    )
                    time.sleep(wait)
                else:
                    print(
                        f"[Slide] Gagal generate AI image scene {slide_number}: {e}"
                    )
                    break  # Error bukan rate-limit, langsung fallback
    else:
        print(f"[Slide] HF_TOKEN tidak ditemukan, pakai fallback slide.")

    # --- 2. FALLBACK: Slide bergaya modern dengan gradient ---
    _create_fallback_slide(visual_desc, slide_number, output_path, W, H)


def _create_fallback_slide(visual_desc: str, slide_number: int, output_path: str, W: int, H: int):
    """Buat slide fallback bergaya modern dengan gradient warna."""
    print(f"[Slide] Membuat fallback slide untuk scene {slide_number}...")

    # Palet warna menarik per scene
    palettes = [
        ("#0f0c29", "#302b63", "#24243e"),  # Deep purple
        ("#134e5e", "#71b280", "#134e5e"),  # Teal-green
        ("#1a1a2e", "#16213e", "#0f3460"),  # Dark blue
        ("#4b6cb7", "#182848", "#4b6cb7"),  # Blue gradient
        ("#11998e", "#38ef7d", "#11998e"),  # Green
    ]
    top_hex, mid_hex, bot_hex = palettes[slide_number % len(palettes)]

    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    top = hex_to_rgb(top_hex)
    bot = hex_to_rgb(bot_hex)

    # Buat gradient vertikal
    img = Image.new("RGB", (W, H))
    for y in range(H):
        t = y / H
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        for x in range(W):
            img.putpixel((x, y), (r, g, b))

    draw = ImageDraw.Draw(img)

    # Font
    try:
        font_small = ImageFont.truetype("arial.ttf", 26)
        font_main  = ImageFont.truetype("arial.ttf", 40)
    except (IOError, OSError):
        font_small = ImageFont.load_default()
        font_main  = ImageFont.load_default()

    # Badge scene number
    badge_x, badge_y = 40, 60
    draw.rounded_rectangle(
        [badge_x - 10, badge_y - 10, badge_x + 130, badge_y + 38],
        radius=16, fill=(255, 255, 255, 40)
    )
    draw.text((badge_x, badge_y), f"Scene {slide_number}", fill=(255, 255, 255), font=font_small)

    # Teks deskripsi visual (tengah)
    wrapped = textwrap.fill(visual_desc, width=22)
    lines   = wrapped.split("\n")
    line_h  = 58
    total_h = len(lines) * line_h
    y_start = (H - total_h) // 2

    for i, line in enumerate(lines):
        bbox   = draw.textbbox((0, 0), line, font=font_main)
        text_w = bbox[2] - bbox[0]
        x      = (W - text_w) // 2
        # Shadow
        draw.text((x + 2, y_start + i * line_h + 2), line, fill=(0, 0, 0, 120), font=font_main)
        draw.text((x, y_start + i * line_h), line, fill="white", font=font_main)

    # Garis dekoratif bawah
    draw.rectangle([(0, H - 6), (W, H)], fill=(255, 255, 255, 80))

    img.save(output_path)
    print(f"[Slide] ✓ Fallback slide scene {slide_number} dibuat.")
