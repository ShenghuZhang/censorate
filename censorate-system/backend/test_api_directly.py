#!/usr/bin/env python3
"""Test notification API directly."""

import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def main():
    print("=" * 60)
    print("TESTING NOTIFICATION API ENDPOINTS")
    print("=" * 60)

    # Test unread count (will use testuser due to security.py fallback)
    print("\n1. Testing GET /api/v1/notifications/unread-count")
    response = client.get("/api/v1/notifications/unread-count")
    print(f"   Status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    print(f"   Response content: {response.content!r}")

    if response.status_code == 200 and response.content:
        try:
            print(f"   Response JSON: {response.json()}")
        except Exception as e:
            print(f"   JSON parse error: {e}")

    # Test getting notifications
    print("\n2. Testing GET /api/v1/notifications")
    response = client.get("/api/v1/notifications")
    print(f"   Status: {response.status_code}")
    print(f"   Response content: {response.content!r}")

    if response.status_code == 200 and response.content:
        try:
            data = response.json()
            print(f"   Number of notifications: {len(data)}")
            for i, notif in enumerate(data):
                print(f"\n   Notification {i+1}:")
                for key, value in notif.items():
                    print(f"     {key}: {value}")
        except Exception as e:
            print(f"   JSON parse error: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
