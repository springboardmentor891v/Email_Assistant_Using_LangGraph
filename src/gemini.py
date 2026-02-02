# Setting up LLM
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
dotenv_path = base_dir / '.env'
load_dotenv(dotenv_path=dotenv_path)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def llm_call(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        contents=prompt,
        config=types.GenerateContentConfig(
            # It forces the model to output raw JSON only
            response_mime_type="application/json" 
        )
    )
    return response.text

def generate_structured_json(self, prompt: str, schema=None) -> str:
    """Forces JSON output (used in your Triage & Draft)"""
    config = types.GenerateContentConfig(
        response_mime_type="application/json"
    )
        
    response = self.client.models.generate_content(
        model=self.model,
        contents=prompt,
        config=config
    )
    return response.tex

# print(llm_call("Hello, Gemini!"))