#!/usr/bin/env python
"""
Test the debug routes endpoint
"""
import requests

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("CHECKING REGISTERED ROUTES VIA DEBUG ENDPOINT")
print("=" * 60)

try:
    response = requests.get(f"{BASE_URL}/debug/routes")
    data = response.json()
    
    # Filter chat routes
    chat_routes = [route for route in data['routes'] if 'chat' in route['rule'].lower()]
    api_chat_routes = [route for route in chat_routes if '/api/chat' in route['rule']]
    
    print(f"\nTotal routes: {len(data['routes'])}")
    print(f"Chat routes: {len(chat_routes)}")
    print(f"API chat routes: {len(api_chat_routes)}")
    
    print("\nAPI Chat Routes:")
    for route in api_chat_routes:
        print(f"  {route['rule']:<50} {route['methods']}")
    
    if len(api_chat_routes) == 0:
        print("  ❌ NO API CHAT ROUTES FOUND!")
    else:
        print(f"\n✅ All {len(api_chat_routes)} API chat routes are registered")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
