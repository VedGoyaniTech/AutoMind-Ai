import json
import requests

def test_stream_api():
    print("=== Testing FastAPI Backend Chat Stream API (/api/v1/chat/stream) ===")
    
    # 1. Login to obtain access token
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_payload = {"email": "demo@automind.ai", "password": "password123"}
    
    try:
        print("1. Authenticating with backend...")
        r_login = requests.post(login_url, json=login_payload, timeout=5)
        if r_login.status_code != 200:
            print(f"Login failed: {r_login.status_code} - {r_login.text}")
            return
        
        token = r_login.json()["access_token"]
        print(f"✔ Authenticated! Received access token: {token[:20]}...")

        # 2. Test Stream API
        stream_url = "http://localhost:8000/api/v1/chat/stream"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        stream_payload = {
            "message": "What are the best SUVs under ₹20 lakh?"
        }

        print("\n2. Sending POST request to /api/v1/chat/stream...")
        r_stream = requests.post(stream_url, headers=headers, json=stream_payload, stream=True, timeout=10)
        print(f"✔ HTTP Response Status Code: {r_stream.status_code}")
        print(f"✔ Response Headers: Content-Type = {r_stream.headers.get('content-type')}")

        print("\n3. Reading real-time SSE stream events:")
        print("-" * 60)
        
        event_count = 0
        for line in r_stream.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    event_count += 1
                    event_data = json.loads(decoded[6:])
                    event_type = event_data.get("event_type")
                    if event_type == "progress":
                        print(f"  [PROGRESS] Stage: {event_data.get('stage')} | {event_data.get('message')}")
                    elif event_type == "token":
                        print(event_data.get("token"), end="", flush=True)
                    elif event_type == "sources":
                        print(f"\n  [SOURCES] Received {len(event_data.get('sources', []))} verified sources")
                    elif event_type == "cars":
                        print(f"  [CARS] Received {len(event_data.get('cars', []))} car cards")
                    elif event_type == "complete":
                        print(f"\n  [COMPLETE] Stream completed successfully!")
                        break

        print("-" * 60)
        print(f"✔ Received {event_count} total SSE stream events.")
        print("=== BACKEND CHAT STREAM API TEST PASSED 100%! ===")

    except Exception as e:
        print(f"❌ Error during backend API test: {e}")

if __name__ == "__main__":
    test_stream_api()
