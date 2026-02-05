#!/usr/bin/env python3
"""
Debug script for institution edit profile issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Institution

def debug_institution_edit():
    """Debug the institution edit profile issue"""
    
    with app.app_context():
        print("🔍 Debugging Institution Edit Profile Issue")
        print("=" * 50)
        
        # Find an institution user - try to find one that might have issues
        institution_users = User.query.filter_by(user_type="3").all()
        
        if not institution_users:
            print("❌ No institution users found in database")
            return False
        
        print(f"✅ Found {len(institution_users)} institution users")
        
        # Check each institution user
        for i, institution_user in enumerate(institution_users):
            print(f"\n👤 Institution User {i+1}: {institution_user.name} ({institution_user.email})")
            
            # Check if institution profile exists
            institution_profile = Institution.query.filter_by(user_id=institution_user.id).first()
            
            if institution_profile:
                print(f"   ✅ Institution profile exists with ID: {institution_profile.id}")
                print(f"   Institution name property: '{institution_profile.name}'")
                print(f"   Institution email property: '{institution_profile.contact_email}'")
                
                # Check if name property returns None or empty
                if not institution_profile.name:
                    print("   ❌ Institution name property is empty/None!")
                if not institution_profile.contact_email:
                    print("   ❌ Institution email property is empty/None!")
                    
            else:
                print("   ⚠️  No institution profile found")
                
                # Create a basic institution profile
                print("   Creating basic institution profile...")
                institution_profile = Institution(
                    user_id=institution_user.id,
                    status="active"
                )
                db.session.add(institution_profile)
                db.session.flush()
                
                institution_user.institution_id = institution_profile.id
                db.session.commit()
                
                print(f"   ✅ Created institution profile with ID: {institution_profile.id}")
                print(f"   Institution name property: '{institution_profile.name}'")
                print(f"   Institution email property: '{institution_profile.contact_email}'")
            
            # Test template variables
            template_name = institution_profile.name if institution_profile else institution_user.name
            template_email = institution_profile.contact_email if institution_profile else institution_user.email
            
            print(f"   📋 Template variables:")
            print(f"      institution_name: '{template_name}'")
            print(f"      email: '{template_email}'")
            
            if not template_name:
                print("   ❌ ISSUE FOUND: institution_name template variable is empty!")
            if not template_email:
                print("   ❌ ISSUE FOUND: email template variable is empty!")
        
        return True

if __name__ == "__main__":
    debug_institution_edit()