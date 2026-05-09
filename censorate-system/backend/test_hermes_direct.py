import httpx
import json

async def test_chat():
    url = "http://localhost:8642/v1/chat/completions"
    payload = {
        "model": "hermes-agent",
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }
    print(f"Testing POST {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Content: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_chat())
