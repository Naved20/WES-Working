#!/usr/bin/env python
"""
Test if the fix worked
"""
import requests

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("TESTING FIX")
print("=" * 60)

routes_to_test = [
    ("/", "GET"),
    ("/signin", "GET"),
    ("/chat", "GET"),
    ("/api/chat/current-user", "GET"),
    ("/api/chat/conversations", "GET"),
    ("/api/chat/allowed-contacts", "GET"),
]

print("\nTesting routes:")
for route, method in routes_to_test:
    try:
        response = requests.get(f"{BASE_URL}{route}", timeout=2)
        status = response.status_code
        if status == 404:
            print(f"  ❌ {route:<40} 404 NOT FOUND")
        elif status in [200, 302, 401]:
            print(f"  ✅ {route:<40} {status}")
        else:
            print(f"  ⚠️  {route:<40} {status}")
    except Exception as e:
        print(f"  ❌ {route:<40} ERROR: {str(e)[:30]}")

print("\n" + "=" * 60)
