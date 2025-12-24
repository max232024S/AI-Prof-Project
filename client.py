import os
import requests
import json
import prompts
def run(role, content, model="openai/gpt-4o"):
    API_KEY = os.getenv("OPENROUTER_API_KEY")

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")



    if role not in prompts.system_prompts:
        raise ValueError(f"Unknown role {role}")
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",   # required by OpenRouter
            "X-Title": "AI Assistant Project",
        },
        json={
            "model": model,
            "messages": [
                
                    prompts.system_prompts[role](),
                    {"role": "user", "content": content}
                
            ]
        }
    )

    response.raise_for_status()  # crashes loudly if request failed
    return (response.json()["choices"][0]["message"]["content"])
