import requests
import json

question = "How would you build the tallest building ever"

url = "https://openrouter.ai/api/v1/chat/completions"
headers = \
{
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
}

payload = \
{
    "model": "openai/gpt-4o",
    "messages": [{"role": "user", "content": question}],
    "stream": True
}

buffer = ""

with requests.post(url, headers=headers, json=payload, stream=True) as r:
    for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
        buffer += chunk
        while True:
            try:
                line_end = buffer.find('\n')
                if line_end == -1:
                    break

                line = buffer[:line_end].strip()
                buffer = buffer[line_end + 1]

                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        data_obj = json.loads(data)
                        content = data_obj["choices"][0]["delta"].get("content")
                        if content:
                            print(content, end="", flush=True)
                    except json.JSONDecodeError:
                            pass
            except Exception:
                        break

