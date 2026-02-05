#!/usr/bin/env python3
"""
Test simple route
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Institution

def test_simple_route():
    """Test simple route"""
    
    with app.test_client() as client:
        with app.app_context():
            print("🧪 Testing Simple Route")
            print("=" * 50)
            
            # Get an institution user
            institution_user = User.query.filter_by(user_type="3").first()
            
            if not institution_user:
                print("❌ No institution users found")
                return
                
            print(f"👤 Testing with user: {institution_user.name} ({institution_user.email})")
            
            # Simulate login session
            with client.session_transaction() as sess:
                sess['email'] = institution_user.email
                sess['user_type'] = '3'
            
            # Test simple route
            response = client.get('/test_institution_name')
            
            print(f"📊 Response status: {response.status_code}")
            print(f"📊 Response text: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_simple_route()