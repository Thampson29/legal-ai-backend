"""List available Gemini models"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("=" * 60)
print("Available Gemini Models")
print("=" * 60)
print()

for model in client.models.list():
    print(f"Model: {model.name}")
    print(f"  Display Name: {model.display_name}")
    print()
