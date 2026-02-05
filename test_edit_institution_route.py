#!/usr/bin/env python3
"""
Test script to simulate accessing the edit institution profile route
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Institution

def test_edit_institution_route():
    """Test the edit institution profile route"""
    
    with app.test_client() as client:
        with app.app_context():
            print("🧪 Testing Edit Institution Profile Route")
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
            
            # Make GET request to edit institution profile
            response = client.get('/editinstitutionprofile')
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Route accessible")
                # Check if institution name is in the response
                response_text = response.get_data(as_text=True)
                
                if 'Not Available' in response_text:
                    print("❌ 'Not Available' found in response - institution name issue detected")
                    
                    # Look for debug info
                    if 'Debug Info:' in response_text:
                        debug_start = response_text.find('Debug Info:')
                        debug_end = response_text.find('</div>', debug_start)
                        debug_info = response_text[debug_start:debug_end]
                        print(f"🔍 Debug info found: {debug_info}")
                else:
                    print("✅ No 'Not Available' found - institution name should be displaying")
                    
                # Look for the institution name in the response
                if institution_user.name in response_text:
                    print(f"✅ Institution name '{institution_user.name}' found in response")
                else:
                    print(f"❌ Institution name '{institution_user.name}' NOT found in response")
                    
            else:
                print(f"❌ Route not accessible: {response.status_code}")
                print(f"Response: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_edit_institution_route()