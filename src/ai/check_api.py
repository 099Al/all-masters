from src.config import settings

from openai import OpenAI

client = OpenAI(api_key=settings.GPT_KEY)

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Привет!"}]
)

print(resp.choices[0].message.content)
