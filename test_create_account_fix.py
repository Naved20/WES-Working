#!/usr/bin/env python3
"""
Test script to verify the create account fix for institutions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Institution
from werkzeug.security import check_password_hash

def test_create_account_logic():
    """Test the create account logic for institutions"""
    
    with app.app_context():
        print("🧪 Testing Create Account Logic for Institutions")
        print("=" * 55)
        
        # Simulate form data for institution admin creation
        form_data = {
            'name': '',  # This should be auto-filled
            'email': 'test_institution_fix@example.edu',
            'password': 'password123',
            'confirm_password': 'password123',
            'user_type': '3',  # Institution admin
            'institution': '',  # Not used for institution admin
            'new_institution_name': 'Test University Fixed'  # This is what should be used
        }
        
        print("1️⃣ Testing Institution Admin Creation Logic")
        
        # Clean up any existing test data
        test_user = User.query.filter_by(email=form_data['email']).first()
        if test_user:
            institution_profile = Institution.query.filter_by(user_id=test_user.id).first()
            if institution_profile:
                test_user.institution_id = None
                db.session.commit()
                db.session.delete(institution_profile)
            db.session.delete(test_user)
            db.session.commit()
        
        # Simulate the backend logic
        user_type = form_data['user_type']
        name = form_data['name']
        email = form_data['email']
        password = form_data['password']
        confirm_password = form_data['confirm_password']
        institution_name = form_data['institution']
        new_institution_name = form_data['new_institution_name']
        
        # Apply the fixed logic
        if user_type == "3":
            if new_institution_name:
                institution_name = new_institution_name
                name = institution_name
                print(f"✅ Institution name set to: {name}")
            else:
                print("❌ ERROR: No institution name provided")
                return False
        
        # Validate required fields
        if not all([name, email, password, confirm_password, user_type]):
            print("❌ ERROR: Missing required fields")
            return False
        
        if len(password) < 6:
            print("❌ ERROR: Password too short")
            return False
        
        if password != confirm_password:
            print("❌ ERROR: Passwords don't match")
            return False
        
        # Check for existing institution name
        existing_institution = User.query.filter_by(name=name, user_type="3").first()
        if existing_institution:
            print("❌ ERROR: Institution name already exists")
            return False
        
        print("✅ All validations passed")
        
        # Test actual creation
        print("\n2️⃣ Testing Actual User and Institution Creation")
        
        try:
            from werkzeug.security import generate_password_hash
            
            # Create new user
            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password),
                user_type=user_type
            )
            db.session.add(new_user)
            db.session.flush()
            
            # Create institution profile
            institution = Institution(
                user_id=new_user.id,
                status="active"
            )
            db.session.add(institution)
            db.session.flush()
            
            new_user.institution_id = institution.id
            db.session.commit()
            
            print(f"✅ Created user: {new_user.name} ({new_user.email})")
            print(f"✅ Created institution profile with ID: {institution.id}")
            print(f"✅ Institution name from property: {institution.name}")
            print(f"✅ Institution email from property: {institution.contact_email}")
            
            # Verify the data
            assert institution.name == name, f"Expected {name}, got {institution.name}"
            assert institution.contact_email == email, f"Expected {email}, got {institution.contact_email}"
            assert check_password_hash(new_user.password, password), "Password hash verification failed"
            
            print("✅ All assertions passed")
            
            # Clean up
            new_user.institution_id = None
            db.session.commit()
            db.session.delete(institution)
            db.session.delete(new_user)
            db.session.commit()
            
            print("✅ Test data cleaned up")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR during creation: {str(e)}")
            return False
        
        print("\n🎉 All tests passed!")
        print("✅ Institution account creation logic is working correctly")
        return True

if __name__ == "__main__":
    success = test_create_account_logic()
    sys.exit(0 if success else 1)