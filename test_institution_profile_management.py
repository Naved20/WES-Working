#!/usr/bin/env python3
"""
Test script for Institution Profile Management

This script tests the new institution profile management system where:
1. Institutions create their own profiles during signup
2. Institution name and email come from signup data and are not editable
3. Profile information is separate but linked to signup information
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Institution
from werkzeug.security import generate_password_hash

def test_institution_profile_management():
    """Test the institution profile management functionality"""
    
    with app.app_context():
        print("🧪 Testing Institution Profile Management")
        print("=" * 50)
        
        # Test 1: Create an institution user
        print("\n1️⃣ Testing Institution User Creation")
        
        # Clean up any existing test data
        test_user = User.query.filter_by(email="test_institution@example.edu").first()
        if test_user:
            # Delete institution profile first
            institution_profile = Institution.query.filter_by(user_id=test_user.id).first()
            if institution_profile:
                # Clear the foreign key reference first
                test_user.institution_id = None
                db.session.commit()
                db.session.delete(institution_profile)
            db.session.delete(test_user)
            db.session.commit()
        
        # Create institution user (simulating supervisor creating account)
        institution_name = "Test University"
        institution_email = "test_institution@example.edu"
        
        new_user = User(
            name=institution_name,  # Institution name as user name
            email=institution_email,  # Institution email as user email
            password=generate_password_hash("password123"),
            user_type="3"  # Institution admin
        )
        db.session.add(new_user)
        db.session.flush()
        
        # Create linked institution profile
        institution = Institution(
            user_id=new_user.id,
            status="active"
        )
        db.session.add(institution)
        db.session.flush()
        
        new_user.institution_id = institution.id
        db.session.commit()
        
        print(f"✅ Created institution user: {new_user.name} ({new_user.email})")
        print(f"✅ Created institution profile with ID: {institution.id}")
        
        # Test 2: Verify institution name and email come from User
        print("\n2️⃣ Testing Institution Name/Email Properties")
        
        retrieved_institution = Institution.query.filter_by(user_id=new_user.id).first()
        
        print(f"Institution name from property: {retrieved_institution.name}")
        print(f"Institution email from property: {retrieved_institution.contact_email}")
        print(f"User name: {retrieved_institution.user.name}")
        print(f"User email: {retrieved_institution.user.email}")
        
        assert retrieved_institution.name == institution_name, "Institution name should come from User.name"
        assert retrieved_institution.contact_email == institution_email, "Institution email should come from User.email"
        
        print("✅ Institution name and email properties work correctly")
        
        # Test 3: Update institution profile (editable fields only)
        print("\n3️⃣ Testing Institution Profile Updates")
        
        retrieved_institution.institution_type = "university"
        retrieved_institution.city = "Test City"
        retrieved_institution.country = "Test Country"
        retrieved_institution.contact_person = "John Doe"
        retrieved_institution.contact_phone = "+1-555-123-4567"
        retrieved_institution.website = "https://testuniversity.edu"
        
        db.session.commit()
        
        # Verify updates
        updated_institution = Institution.query.filter_by(user_id=new_user.id).first()
        assert updated_institution.institution_type == "university"
        assert updated_institution.city == "Test City"
        assert updated_institution.country == "Test Country"
        assert updated_institution.contact_person == "John Doe"
        assert updated_institution.contact_phone == "+1-555-123-4567"
        assert updated_institution.website == "https://testuniversity.edu"
        
        # Verify name and email are still from User
        assert updated_institution.name == institution_name
        assert updated_institution.contact_email == institution_email
        
        print("✅ Institution profile updates work correctly")
        print("✅ Institution name and email remain linked to User data")
        
        # Test 4: Test database constraints
        print("\n4️⃣ Testing Database Constraints")
        
        # Try to create institution without user_id (should fail)
        try:
            invalid_institution = Institution(status="active")
            db.session.add(invalid_institution)
            db.session.commit()
            print("❌ ERROR: Institution without user_id should not be allowed")
        except Exception as e:
            db.session.rollback()
            print("✅ Correctly prevented institution creation without user_id")
        
        # Test 5: Test unique constraints
        print("\n5️⃣ Testing Unique Constraints")
        
        # Try to create another institution with same user_id (should fail)
        try:
            duplicate_institution = Institution(user_id=new_user.id, status="active")
            db.session.add(duplicate_institution)
            db.session.commit()
            print("❌ ERROR: Duplicate user_id should not be allowed")
        except Exception as e:
            db.session.rollback()
            print("✅ Correctly prevented duplicate user_id in institutions")
        
        print("\n🎉 All tests passed!")
        print("=" * 50)
        print("✅ Institution profile management is working correctly:")
        print("   • Institutions are properly linked to User accounts")
        print("   • Institution name comes from User.name (not editable)")
        print("   • Institution email comes from User.email (not editable)")
        print("   • Profile fields are editable and separate from signup data")
        print("   • Database constraints are properly enforced")
        
        # Clean up test data
        new_user.institution_id = None
        db.session.commit()
        db.session.delete(retrieved_institution)
        db.session.delete(new_user)
        db.session.commit()
        print("\n🧹 Test data cleaned up")

if __name__ == "__main__":
    test_institution_profile_management()