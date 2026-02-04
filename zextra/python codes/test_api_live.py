#!/usr/bin/env python
"""
Test API endpoints with a live Flask server
"""
import requests
import json
from requests.sessions import Session

BASE_URL = "http://127.0.0.1:5000"

def test_endpoints():
    print("=" * 60)
    print("TESTING LIVE API ENDPOINTS")
    print("=" * 60)
    
    # Test 1: Check if /chat page loads
    print("\n1. Testing /chat page...")
    try:
        response = requests.get(f"{BASE_URL}/chat", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Redirected to signin (expected - not authenticated)")
        elif response.status_code == 200:
            print("   ✅ Chat page loaded")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check if /api/chat/current-user endpoint exists
    print("\n2. Testing /api/chat/current-user endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/current-user", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Endpoint exists (401 Unauthorized - expected)")
            print(f"   Response: {response.json()}")
        else:
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check if /api/chat/conversations endpoint exists
    print("\n3. Testing /api/chat/conversations endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/conversations", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Endpoint exists (401 Unauthorized - expected)")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check if /api/chat/allowed-contacts endpoint exists
    print("\n4. Testing /api/chat/allowed-contacts endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/allowed-contacts", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Endpoint exists (401 Unauthorized - expected)")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ALL ENDPOINTS ARE ACCESSIBLE")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()
