"""
List available Gemini models using google.generativeai
"""
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Configure the API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("📋 Available Gemini models:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Display name: {model.display_name}")
        print()
