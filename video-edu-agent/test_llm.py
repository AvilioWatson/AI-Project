import os
from dotenv import load_dotenv

load_dotenv()

print("Mulai test Gemini...")
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY tidak ditemukan di .env!")
    exit(1)

print(f"Key loaded: {api_key[:5]}...{api_key[-5:]}")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Balas dengan kalimat: 'Halo Dunia'",
    )
    print("✓ GEMINI SUCCESS!")
    print("Response:", response.text)
except Exception as e:
    import traceback
    print("❌ GEMINI FAIL:")
    traceback.print_exc()
