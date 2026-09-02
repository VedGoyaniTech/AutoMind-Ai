import requests
import json
from app.core.config import settings

def test_nvidia_key():
    url = f"{settings.NVIDIA_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    models_to_test = [
        settings.NVIDIA_MODEL_ID,
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "deepseek-ai/deepseek-r1",
        "qwen/qwen2.5-72b-instruct"
    ]

    print("=== TESTING NVIDIA API KEY INTERNALLY ===")
    print(f"API Key: {settings.NVIDIA_API_KEY[:10]}...{settings.NVIDIA_API_KEY[-6:]}")
    print(f"Base URL: {settings.NVIDIA_BASE_URL}")

    for model in models_to_test:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Say hello in one word."}
            ],
            "max_tokens": 10,
            "stream": False
        }
        try:
            print(f"\nTesting Model: {model}...")
            resp = requests.post(url, headers=headers, json=payload, timeout=10.0)
            print(f"Status Code: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"SUCCESS ✅ Response: {content.strip()}")
            else:
                print(f"FAILED ❌ Error Body: {resp.text[:300]}")
        except Exception as e:
            print(f"EXCEPTION ❌ {e}")

if __name__ == "__main__":
    test_nvidia_key()
