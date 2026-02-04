#!/usr/bin/env python
"""
Debug script to check if routes are being registered
"""
import sys
sys.path.insert(0, '.')

# Import the app
from app import app

print("=" * 60)
print("CHECKING REGISTERED ROUTES")
print("=" * 60)

# Get all routes
routes = []
for rule in app.url_map.iter_rules():
    if 'chat' in rule.rule.lower():
        routes.append({
            'rule': rule.rule,
            'methods': rule.methods,
            'endpoint': rule.endpoint
        })

print(f"\nFound {len(routes)} chat-related routes:\n")

for route in sorted(routes, key=lambda x: x['rule']):
    methods = ', '.join(sorted(route['methods'] - {'HEAD', 'OPTIONS'}))
    print(f"  {route['rule']:<50} [{methods}]")
    print(f"    Endpoint: {route['endpoint']}")

print("\n" + "=" * 60)

# Check specifically for API routes
api_routes = [r for r in routes if '/api/chat' in r['rule']]
print(f"\nAPI Routes: {len(api_routes)}")
for route in api_routes:
    print(f"  ✅ {route['rule']}")

if len(api_routes) == 0:
    print("  ❌ NO API ROUTES FOUND!")
else:
    print(f"\n✅ All {len(api_routes)} API routes are registered")

print("=" * 60)
