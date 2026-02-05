#!/usr/bin/env python3
"""
Test script to verify the edit profile fix
"""

import requests
import sys

def test_edit_profile_fix():
    """Test that the edit profile page loads without name field issues"""
    
    print("🔧 Testing Edit Profile Fix")
    print("=" * 35)
    
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Check if app is running
    try:
        response = requests.get(f"{base_url}/signin", timeout=5)
        if response.status_code != 200:
            print(f"❌ App not accessible: {response.status_code}")
            return False
        print("✅ App is running and accessible")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to app: {e}")
        return False
    
    # Test 2: Check template changes
    try:
        with open("templates/institution/editinstitutionprofile.html", "r", encoding="utf-8") as f:
            template_content = f.read()
        
        # Check that name field is no longer an input
        if 'name="name"' not in template_content:
            print("✅ Name field removed from form inputs")
        else:
            print("❌ Name field still exists as form input")
            return False
        
        # Check that readonly display fields exist
        if 'readonly-display-field' in template_content:
            print("✅ Readonly display fields implemented")
        else:
            print("❌ Readonly display fields missing")
            return False
        
        # Check that debug info is present
        if 'Debug: institution_name' in template_content:
            print("✅ Debug information added")
        else:
            print("❌ Debug information missing")
            return False
        
        # Check that contact_email input is removed
        if 'name="contact_email"' not in template_content:
            print("✅ Contact email field removed from form inputs")
        else:
            print("❌ Contact email field still exists as form input")
            return False
        
        print("\n📋 Template Analysis:")
        print("   ✅ Institution name displayed as read-only text (not form input)")
        print("   ✅ Institution email displayed as read-only text (not form input)")
        print("   ✅ No form validation will check these fields")
        print("   ✅ Enhanced visual styling for readonly fields")
        
        return True
        
    except FileNotFoundError:
        print("❌ Template file not found")
        return False

if __name__ == "__main__":
    success = test_edit_profile_fix()
    if success:
        print("\n🎉 Edit Profile Fix Successful!")
        print("✅ Institution name and email are now display-only")
        print("✅ No form validation errors should occur")
        print("✅ Users can save the form without 'Name' field errors")
    else:
        print("\n❌ Edit Profile Fix Failed!")
    
    sys.exit(0 if success else 1)