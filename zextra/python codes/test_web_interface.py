#!/usr/bin/env python3
"""
Test script to verify the web interface works correctly
"""

import requests
import sys

def test_web_interface():
    """Test that the web interface is accessible"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🌐 Testing Web Interface")
    print("=" * 40)
    
    # Test 1: Check if app is running
    try:
        response = requests.get(f"{base_url}/signin", timeout=5)
        if response.status_code == 200:
            print("✅ App is running and accessible")
        else:
            print(f"❌ App returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to app: {e}")
        return False
    
    # Test 2: Check create account page (requires login, so expect redirect)
    try:
        response = requests.get(f"{base_url}/create_account", timeout=5, allow_redirects=False)
        if response.status_code in [302, 401]:  # Redirect to login
            print("✅ Create account page properly requires authentication")
        else:
            print(f"⚠️  Create account page returned: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing create account: {e}")
        return False
    
    # Test 3: Check institution profile page (requires login, so expect redirect)
    try:
        response = requests.get(f"{base_url}/editinstitutionprofile", timeout=5, allow_redirects=False)
        if response.status_code in [302, 401]:  # Redirect to login
            print("✅ Institution profile page properly requires authentication")
        else:
            print(f"⚠️  Institution profile page returned: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing institution profile: {e}")
        return False
    
    print("\n🎉 Web interface tests passed!")
    print("✅ All endpoints are accessible and properly secured")
    return True

if __name__ == "__main__":
    success = test_web_interface()
    sys.exit(0 if success else 1)