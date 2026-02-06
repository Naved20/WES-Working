#!/usr/bin/env python3
"""
Debug script for institution edit profile session issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Institution

def debug_session_institution():
    """Debug the institution edit profile session issue"""
    
    with app.app_context():
        print("🔍 Debugging Institution Session Issue")
        print("=" * 50)
        
        # Test the exact scenario from the route
        institution_users = User.query.filter_by(user_type="3").all()
        
        for institution_user in institution_users:
            print(f"\n👤 Testing user: {institution_user.name} ({institution_user.email})")
            
            # Simulate the exact code from editinstitutionprofile route
            user = User.query.filter_by(email=institution_user.email).first()
            if not user:
                print("   ❌ User not found")
                continue
                
            print(f"   ✅ User found: {user.name}")
            
            # Get or create institution profile (exact code from route)
            institution = Institution.query.filter_by(user_id=user.id).first()
            
            if institution:
                print(f"   ✅ Institution profile found: ID {institution.id}")
                print(f"   Institution.user: {institution.user}")
                print(f"   Institution.user.name: {institution.user.name if institution.user else 'None'}")
                print(f"   Institution.name property: '{institution.name}'")
                
                # Test the template variable assignment
                template_institution_name = institution.name if institution else user.name
                print(f"   📋 Template institution_name: '{template_institution_name}'")
                
                if not template_institution_name:
                    print("   ❌ ISSUE: Template institution_name is empty!")
                    
                    # Debug the relationship
                    print(f"   🔍 Debugging relationship:")
                    print(f"      institution.user_id: {institution.user_id}")
                    print(f"      user.id: {user.id}")
                    print(f"      institution.user is None: {institution.user is None}")
                    
                    # Try to reload the relationship
                    db.session.refresh(institution)
                    print(f"   After refresh - institution.user: {institution.user}")
                    print(f"   After refresh - institution.name: '{institution.name}'")
                    
            else:
                print("   ⚠️  No institution profile found")
                template_institution_name = user.name
                print(f"   📋 Template institution_name (fallback): '{template_institution_name}'")

if __name__ == "__main__":
    debug_session_institution()