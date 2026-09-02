import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

print("API key loaded:", bool(os.getenv("GEMINI_API_KEY")))
print("Model:", os.getenv("GEMINI_MODEL", "gemini-3.6-flash"))

client = genai.Client()
response = client.models.generate_content(
    model=os.getenv("GEMINI_MODEL", "gemini-3.7-flash"),
    contents="Say hello in one sentence.",
)

print("Response:", response.text)
