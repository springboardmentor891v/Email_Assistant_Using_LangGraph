import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

def groq_judge(prompt: str) -> dict:
    completion = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=512
    )

    return json.loads(
        completion.choices[0].message.content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

