import sys
import asyncio
import httpx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.remote_agent import RemoteAgent

async def check_status():
    db = SessionLocal()
    print("=" * 60)
    print("Checking Local-Hermes Agent Status...")
    print("=" * 60)
    
    agent = db.query(RemoteAgent).filter(RemoteAgent.name == "Local-Hermes").first()
    
    if not agent:
        print("❌ Agent 'Local-Hermes' not found in database.")
        return

    print(f"DB Record: Found")
    print(f"Name: {agent.name}")
    print(f"Type: {agent.agent_type}")
    print(f"Endpoint: {agent.endpoint_url}")
    print(f"Status: {agent.status}")
    
    print("\nTesting connectivity to endpoint...")
    try:
        # Check the base URL or the completions endpoint
        base_url = agent.endpoint_url.split('/v1')[0] + '/v1/models'
        async with httpx.AsyncClient() as client:
            # We use a short timeout
            response = await client.get(base_url, timeout=5.0)
            if response.status_code == 200:
                print(f"Connectivity: Success (HTTP 200)")
                print(f"Response: {response.json()}")
            else:
                print(f"Connectivity: Warning (HTTP {response.status_code})")
                print(f"Detail: {response.text}")
    except Exception as e:
        print(f"Connectivity: Failed")
        print(f"Error: {e}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(check_status())
