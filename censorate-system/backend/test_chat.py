"""Test chat functionality directly."""

import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.remote_agent import RemoteAgent
from app.core.security import decrypt_api_key

# Test decryption
db = SessionLocal()
try:
    agent = db.query(RemoteAgent).filter(RemoteAgent.name == 'Hermes').first()
    print(f"Agent: {agent.name}")
    print(f"Encrypted API key: {agent._api_key[:50]}..." if agent._api_key else "No API key")
    print(f"Decrypted API key: {agent.api_key}")

    # Test direct API call
    import httpx
    import json

    chat_url = f"{agent.endpoint_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {agent.api_key}",
        "X-Hermes-Session-Id": "test-session-123"
    }

    hermes_request = {
        "model": "hermes-agent",
        "messages": [{"role": "user", "content": "Hello!"}],
        "stream": False
    }

    print(f"\nTesting direct call to: {chat_url}")
    print(f"Headers: {dict(Authorization=headers['Authorization'][:50] + '...', **{k:v for k,v in headers.items() if k != 'Authorization'})}")
    print(f"Request: {json.dumps(hermes_request, indent=2)}")

    timeout = httpx.Timeout(60.0, connect=5.0)
    response = httpx.post(chat_url, headers=headers, json=hermes_request, timeout=timeout)
    print(f"\nResponse status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
