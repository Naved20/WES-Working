#!/usr/bin/env python3
"""
Direct test of the route logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Institution

def test_direct_route():
    """Test the route logic directly"""
    
    with app.app_context():
        print("🧪 Testing Route Logic Directly")
        print("=" * 50)
        
        # Get an institution user
        institution_user = User.query.filter_by(user_type="3").first()
        
        if not institution_user:
            print("❌ No institution users found")
            return
            
        print(f"👤 Testing with user: {institution_user.name} ({institution_user.email})")
        print(f"   User ID: {institution_user.id}")
        print(f"   User name type: {type(institution_user.name)}")
        print(f"   User name repr: {repr(institution_user.name)}")
        
        # Simulate the exact route logic
        user = User.query.filter_by(email=institution_user.email).first()
        print(f"✅ User found: {user.name}")
        print(f"   User name type: {type(user.name)}")
        print(f"   User name repr: {repr(user.name)}")
        
        # Get institution profile
        institution = Institution.query.filter_by(user_id=user.id).first()
        
        if institution:
            print(f"✅ Institution profile found: ID {institution.id}")
        else:
            print("⚠️  No institution profile found")
        
        # Test the template variable assignment (exact code from route)
        institution_name = user.name  # Institution name is always from the User (signup_details) table
        institution_email = user.email  # Institution email is always from the User (signup_details) table
        
        print(f"📋 Template variables:")
        print(f"   institution_name: {repr(institution_name)}")
        print(f"   institution_email: {repr(institution_email)}")
        print(f"   institution_name type: {type(institution_name)}")
        print(f"   institution_name bool: {bool(institution_name)}")
        print(f"   institution_name is None: {institution_name is None}")
        print(f"   institution_name == '': {institution_name == ''}")
        
        # Test Jinja2 template logic
        template_result = institution_name or 'Not Available'
        print(f"   Template result (name or 'Not Available'): {repr(template_result)}")

if __name__ == "__main__":
    test_direct_route()