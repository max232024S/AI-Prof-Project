import os
import requests
import json

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set")

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",   # required by OpenRouter
        "X-Title": "VSCode Python Project",
    },
    json={
        "model": "openai/gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": "Whats a good restaurant to go to?"
            }
        ]
    }
)

response.raise_for_status()  # crashes loudly if request failed
print (response.json()["choices"][0]["message"]["content"])
