from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import os


def render_video(scenes: list, audio_dir: str, slide_dir: str, output_path: str):
    """
    Render video final dari audio + slide per scene.
    Dioptimalkan: preset=fast, threads=4 untuk render lebih cepat.
    """
    clips = []

    for scene in scenes:
        sid        = scene["scene_id"]
        audio_file = os.path.join(audio_dir, f"scene_{sid}.mp3")
        slide_file = os.path.join(slide_dir, f"scene_{sid}.png")

        audio    = AudioFileClip(audio_file)
        duration = audio.duration

        clip = (
            ImageClip(slide_file)
            .with_duration(duration)
            .with_audio(audio)
        )
        clips.append(clip)
        print(f"[Video] ✓ Scene {sid} siap ({duration:.1f}s)")

    print(f"[Video] Menggabungkan {len(clips)} scene dan merender video...")
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="fast",       # Render lebih cepat
        threads=4,           # Manfaatkan multi-core
        logger=None,         # Suppress verbose moviepy log
    )
    final.close()
    print(f"[Video] ✓ Video selesai: {output_path}")
