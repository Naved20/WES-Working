#!/usr/bin/env python3
"""
Test template variables directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Institution

def test_template_vars():
    """Test template variables directly"""
    
    with app.test_client() as client:
        with app.app_context():
            print("🧪 Testing Template Variables")
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
                response_text = response.get_data(as_text=True)
                
                # Look for the actual template variable values
                print("\n🔍 Searching for template variables in response:")
                
                # Look for the readonly display value
                if 'readonly-display-value' in response_text:
                    start = response_text.find('<div class="readonly-display-value">')
                    if start != -1:
                        end = response_text.find('</div>', start)
                        if end != -1:
                            display_value = response_text[start:end]
                            print(f"   Readonly display value: {display_value}")
                
                # Look for debug info more carefully
                debug_start = response_text.find('name = "')
                if debug_start != -1:
                    debug_end = response_text.find('"', debug_start + 8)
                    if debug_end != -1:
                        debug_value = response_text[debug_start + 8:debug_end]
                        print(f"   Debug name value: '{debug_value}'")
                
                # Check if the template is actually using the variable
                if 'Not Available' in response_text:
                    print("   ❌ 'Not Available' found - template variable is empty")
                else:
                    print("   ✅ 'Not Available' not found - template variable should have value")
                    
                # Look for the institution name in the readonly field
                readonly_start = response_text.find('readonly-display-value')
                if readonly_start != -1:
                    readonly_section = response_text[readonly_start:readonly_start + 200]
                    print(f"   Readonly section: {readonly_section}")

if __name__ == "__main__":
    test_template_vars()