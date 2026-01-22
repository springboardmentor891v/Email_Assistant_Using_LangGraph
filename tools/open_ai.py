# tools/openai_agent.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def generate_reply(subject, sender, body):
    prompt = f"""
You are a professional email assistant.

Subject: {subject}
From: {sender}

Email:
{body}

Write a polite, professional reply.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()
