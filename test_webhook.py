#!/usr/bin/env python3
"""Test script to trigger agent update and see if webhook works."""

import httpx
import json
import time

# Agent ID from database
agent_id = "bf12d1ff-5b69-4808-a56f-003a9d2a3234"

# First, let's get the current agent data
print("Getting current agent data...")
response = httpx.get(f"http://localhost:8216/api/v1/remote-agents/{agent_id}")
print(f"Response: {response.status_code}")
current_data = response.json()
print(f"Current capabilities: {current_data.get('capabilities', [])}")

# Let's remove one skill to trigger a change
new_capabilities = [cap for cap in current_data.get('capabilities', []) if cap != 'risk-identification']
print(f"\nUpdating to capabilities: {new_capabilities}")

update_data = {
    "capabilities": new_capabilities
}

response = httpx.put(f"http://localhost:8216/api/v1/remote-agents/{agent_id}", json=update_data)
print(f"\nUpdate response: {response.status_code}")
if response.status_code == 200:
    print("Update successful!")
    print("Webhook should have been triggered.")

print("\nWaiting a bit for webhook processing...")
time.sleep(2)

print("\nNow let's add the skill back...")
new_capabilities.append('risk-identification')
update_data = {
    "capabilities": new_capabilities
}

response = httpx.put(f"http://localhost:8216/api/v1/remote-agents/{agent_id}", json=update_data)
print(f"Update response: {response.status_code}")
if response.status_code == 200:
    print("Update successful!")
    print("Webhook should have been triggered again.")
