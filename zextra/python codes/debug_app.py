#!/usr/bin/env python
"""
Debug script to check Flask app routes
"""
import sys
sys.path.insert(0, '.')

from app import app

print("=" * 60)
print("FLASK APP ROUTES DEBUG")
print("=" * 60)

# Get all routes
all_routes = list(app.url_map.iter_rules())
print(f"\nTotal routes: {len(all_routes)}")

# Get chat routes
chat_routes = [r for r in all_routes if 'chat' in r.rule.lower()]
print(f"Chat routes: {len(chat_routes)}")

# Get API chat routes
api_routes = [r for r in all_routes if '/api/chat' in r.rule]
print(f"API chat routes: {len(api_routes)}")

print("\nAPI Chat Routes:")
for route in sorted(api_routes, key=lambda x: x.rule):
    methods = ', '.join(sorted(route.methods - {'HEAD', 'OPTIONS'}))
    print(f"  {route.rule:<50} [{methods}]")
    print(f"    Endpoint: {route.endpoint}")
    print(f"    Function: {route.endpoint}")

print("\n" + "=" * 60)

# Now start the app
print("\nStarting Flask app...")
print("=" * 60)
app.run(debug=False, host='0.0.0.0', port=5000)
