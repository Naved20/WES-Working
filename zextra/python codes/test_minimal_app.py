#!/usr/bin/env python
"""
Minimal test app to verify routes work
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/test", methods=["GET"])
def test_route():
    return jsonify({"success": True, "message": "Test route works"})

if __name__ == "__main__":
    print("Routes registered:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    app.run(debug=False, port=5001)
