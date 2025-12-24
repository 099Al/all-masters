from openai import OpenAI
from src.config import settings

openai_api_key = settings.GPT_KEY

client = OpenAI(api_key=settings.GPT_KEY)


def ai_query(prompt: str):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Return the answer strictly as JSON. Do not include any extra text."
            },
            {"role": "user", "content": prompt
             }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return resp