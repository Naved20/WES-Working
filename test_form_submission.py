#!/usr/bin/env python3
"""
Test form submission without name field
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Institution

def test_form_submission():
    """Test form submission"""
    
    with app.test_client() as client:
        with app.app_context():
            print("🧪 Testing Form Submission")
            print("=" * 60)
            
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
            
            # Prepare form data (without name field)
            form_data = {
                'contact_person': 'John Doe',
                'contact_phone': '+1-555-1234',
                'address': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'website': 'https://example.com',
                'email_domain': 'example.com',
                'institution_type': 'university'
            }
            
            # Make POST request
            response = client.post('/editinstitutionprofile', data=form_data, follow_redirects=True)
            
            print(f"📊 Response status: {response.status_code}")
            
            response_text = response.get_data(as_text=True)
            
            # Check for error messages
            if 'Please fill all mandatory fields' in response_text:
                print("❌ Error: 'Please fill all mandatory fields' message found")
                # Extract the error message
                if 'Name' in response_text:
                    print("   ❌ Error mentions 'Name' field")
                else:
                    print("   ✅ Error does not mention 'Name' field")
            else:
                print("✅ No 'Please fill all mandatory fields' error")
            
            # Check for success message
            if 'successfully' in response_text.lower() or 'updated' in response_text.lower():
                print("✅ Success message found")
            else:
                print("⚠️  No success message found")

if __name__ == "__main__":
    test_form_submission()