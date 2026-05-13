import edge_tts
import asyncio

async def _generate(text: str, output_path: str, language: str):
    voice = "id-ID-GadisNeural" if language == "id" else "en-US-JennyNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_audio(text: str, output_path: str, language: str = "id"):
    asyncio.run(_generate(text, output_path, language))
