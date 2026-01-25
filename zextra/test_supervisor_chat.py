#!/usr/bin/env python
"""
Test supervisor chat with authentication
"""
import requests
from requests.sessions import Session

BASE_URL = "http://127.0.0.1:5000"

def test_supervisor_chat():
    print("=" * 60)
    print("TESTING SUPERVISOR CHAT")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = Session()
    
    # Test 1: Login as supervisor
    print("\n1. Logging in as supervisor (WES)...")
    login_data = {
        "email": "wes@example.com",
        "password": "password123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/signin", data=login_data, allow_redirects=True)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Get current user
    print("\n2. Getting current user...")
    try:
        response = session.get(f"{BASE_URL}/api/chat/current-user")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Current user: {data.get('user_name')} (ID: {data.get('user_id')}, Type: {data.get('user_type')})")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get conversations
    print("\n3. Getting conversations...")
    try:
        response = session.get(f"{BASE_URL}/api/chat/conversations")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            conversations = data.get('conversations', [])
            print(f"   ✅ Found {len(conversations)} conversations")
            for conv in conversations[:3]:
                print(f"      - {conv['other_user_name']}: {conv['last_message']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get allowed contacts
    print("\n4. Getting allowed contacts...")
    try:
        response = session.get(f"{BASE_URL}/api/chat/allowed-contacts")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            contacts = data.get('contacts', [])
            print(f"   ✅ Found {len(contacts)} allowed contacts")
            
            # Count by role
            mentors = [c for c in contacts if c['type'] == '1']
            mentees = [c for c in contacts if c['type'] == '2']
            print(f"      - Mentors: {len(mentors)}")
            print(f"      - Mentees: {len(mentees)}")
            
            # Show first 5
            print(f"\n   First 5 contacts:")
            for contact in contacts[:5]:
                print(f"      - {contact['name']} ({contact['role']})")
            if len(contacts) > 5:
                print(f"      ... and {len(contacts) - 5} more")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ SUPERVISOR CHAT TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_supervisor_chat()
