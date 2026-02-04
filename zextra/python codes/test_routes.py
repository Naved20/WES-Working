#!/usr/bin/env python
"""Test if all chat routes are registered"""

from app import app

print("=" * 70)
print("CHECKING REGISTERED ROUTES")
print("=" * 70)

# Get all routes
routes = []
for rule in app.url_map.iter_rules():
    if 'chat' in rule.rule:
        routes.append({
            'rule': rule.rule,
            'methods': rule.methods,
            'endpoint': rule.endpoint
        })

print(f"\nFound {len(routes)} chat routes:\n")

for route in sorted(routes, key=lambda x: x['rule']):
    methods = ', '.join(sorted(route['methods'] - {'HEAD', 'OPTIONS'}))
    print(f"✅ {route['rule']:<40} [{methods}]")

print("\n" + "=" * 70)

if len(routes) >= 7:
    print("✅ All chat routes registered!")
else:
    print(f"❌ Expected 7+ routes, found {len(routes)}")

print("=" * 70)
