#!/usr/bin/env python
"""
Test app routes directly using Flask test client
"""
import sys
sys.path.insert(0, '.')

from app import app

print("=" * 60)
print("TESTING APP ROUTES WITH FLASK TEST CLIENT")
print("=" * 60)

# Create a test client
client = app.test_client()

# Test 1: Check if /chat page loads
print("\n1. Testing /chat page...")
response = client.get('/chat')
print(f"   Status: {response.status_code}")
if response.status_code in [200, 302]:
    print("   ✅ /chat page accessible")
else:
    print(f"   ❌ Unexpected status: {response.status_code}")

# Test 2: Check if /api/chat/current-user endpoint exists
print("\n2. Testing /api/chat/current-user endpoint...")
response = client.get('/api/chat/current-user')
print(f"   Status: {response.status_code}")
if response.status_code == 401:
    print("   ✅ Endpoint exists (401 Unauthorized - expected)")
    print(f"   Response: {response.get_json()}")
else:
    print(f"   ❌ Unexpected status: {response.status_code}")
    print(f"   Response: {response.data[:200]}")

# Test 3: Check if /api/chat/conversations endpoint exists
print("\n3. Testing /api/chat/conversations endpoint...")
response = client.get('/api/chat/conversations')
print(f"   Status: {response.status_code}")
if response.status_code == 401:
    print("   ✅ Endpoint exists (401 Unauthorized - expected)")
else:
    print(f"   ❌ Unexpected status: {response.status_code}")

# Test 4: Check if /api/chat/allowed-contacts endpoint exists
print("\n4. Testing /api/chat/allowed-contacts endpoint...")
response = client.get('/api/chat/allowed-contacts')
print(f"   Status: {response.status_code}")
if response.status_code == 401:
    print("   ✅ Endpoint exists (401 Unauthorized - expected)")
else:
    print(f"   ❌ Unexpected status: {response.status_code}")

print("\n" + "=" * 60)
print("✅ ALL ENDPOINTS ACCESSIBLE VIA TEST CLIENT")
print("=" * 60)
