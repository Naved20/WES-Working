#!/usr/bin/env python3
"""
Test institution name display for all institution users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def test_all_institutions():
    """Test institution name display for all institution users"""
    
    with app.test_client() as client:
        with app.app_context():
            print("🧪 Testing Institution Name Display for All Users")
            print("=" * 60)
            
            # Get all institution users
            institution_users = User.query.filter_by(user_type="3").all()
            
            if not institution_users:
                print("❌ No institution users found")
                return
                
            print(f"✅ Found {len(institution_users)} institution users\n")
            
            for user in institution_users:
                print(f"👤 Testing: {user.name} ({user.email})")
                
                # Simulate login session
                with client.session_transaction() as sess:
                    sess['email'] = user.email
                    sess['user_type'] = '3'
                
                # Make GET request to edit institution profile
                response = client.get('/editinstitutionprofile')
                
                if response.status_code == 200:
                    response_text = response.get_data(as_text=True)
                    
                    # Look for the readonly display value
                    if 'readonly-display-value' in response_text:
                        start = response_text.find('<div class="readonly-display-value">')
                        if start != -1:
                            end = response_text.find('</div>', start)
                            if end != -1:
                                display_value = response_text[start + 36:end].strip()
                                
                                if display_value == user.name:
                                    print(f"   ✅ Name displayed correctly: '{display_value}'")
                                elif display_value == 'Not Available':
                                    print(f"   ❌ Name showing 'Not Available' instead of '{user.name}'")
                                else:
                                    print(f"   ⚠️  Name showing '{display_value}' instead of '{user.name}'")
                    
                    # Check for email
                    if f'{{ email or' in response_text or user.email in response_text:
                        print(f"   ✅ Email field present")
                    else:
                        print(f"   ❌ Email field missing")
                else:
                    print(f"   ❌ Response status: {response.status_code}")
                
                print()

if __name__ == "__main__":
    test_all_institutions()