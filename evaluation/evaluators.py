import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def judge_reply(email_text, agent_reply):
    prompt = f"""
You are evaluating an AI email assistant.

Email:
{email_text}

Agent Reply:
{agent_reply}

Score the reply from 0 to 10 on:
- relevance
- politeness
- correctness

Return JSON only.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content
