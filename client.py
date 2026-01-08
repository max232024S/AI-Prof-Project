import os
import requests
import json
import prompts
import numpy as np

API_KEY = os.getenv("OPENROUTER_API_KEY") #pull environmental var

def run(role, content, model="google/gemini-2.0-flash-001"):

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
    raw = response.json()["choices"][0]["message"]["content"] #raw json string format
    #data = json.loads(raw) #converted to python dictionary and returned
    return raw



def embed(chunks): #returns list of arrays of embeddings - note these need to be converted to BLOBS before INSERTION
    url = "https://openrouter.ai/api/v1/embeddings"

    payload = {
        "input": chunks,
        "model": "text-embedding-3-large"
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    #embeddings = [np.array(obj) in response['embedding'] for obj in response.json()['data']]
    embeddings = [np.array(item['embedding']) for item in response.json()['data']]
    return embeddings
    
    

