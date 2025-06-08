import requests

AI_API_URL = "https://ai.hackclub.com/chat/completions"

def query_ai_api(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(AI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            return "Error: Unexpected response format from AI API."
    return "Error: AI API did not respond successfully."
