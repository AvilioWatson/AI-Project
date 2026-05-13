def seconds_to_srt_time(s: float) -> str:
    h   = int(s // 3600)
    m   = int((s % 3600) // 60)
    sec = int(s % 60)
    ms  = int((s - int(s)) * 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"

def generate_srt(scenes: list, output_path: str):
    srt_lines = []
    current_time = 0.0

    for i, scene in enumerate(scenes, 1):
        start = current_time
        end   = current_time + scene["duration_sec"]

        srt_lines.append(str(i))
        srt_lines.append(f"{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}")
        srt_lines.append(scene["subtitle"])
        srt_lines.append("")

        current_time = end

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
