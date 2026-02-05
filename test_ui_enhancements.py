#!/usr/bin/env python3
"""
Test script to verify UI enhancements for institution profile management
"""

import requests
import sys

def test_ui_enhancements():
    """Test that the UI enhancements are present in the templates"""
    
    print("🎨 Testing UI Enhancements for Institution Profile")
    print("=" * 55)
    
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
    
    # Test 2: Check template files for UI enhancements
    print("\n2️⃣ Checking Template Files for UI Enhancements")
    
    # Check edit profile template
    try:
        with open("templates/institution/editinstitutionprofile.html", "r", encoding="utf-8") as f:
            edit_template_content = f.read()
        
        # Check for enhanced messaging
        enhancements_found = []
        
        if "Official Institution Name" in edit_template_content:
            enhancements_found.append("✅ Official Institution Name label")
        else:
            enhancements_found.append("❌ Missing Official Institution Name label")
        
        if "Official Institution Email" in edit_template_content:
            enhancements_found.append("✅ Official Institution Email label")
        else:
            enhancements_found.append("❌ Missing Official Institution Email label")
        
        if "readonly-hint" in edit_template_content:
            enhancements_found.append("✅ Enhanced readonly hints")
        else:
            enhancements_found.append("❌ Missing enhanced readonly hints")
        
        if "info-banner" in edit_template_content:
            enhancements_found.append("✅ Information banner")
        else:
            enhancements_found.append("❌ Missing information banner")
        
        if "official identifiers set during account creation" in edit_template_content:
            enhancements_found.append("✅ Clear explanation about official identifiers")
        else:
            enhancements_found.append("❌ Missing explanation about official identifiers")
        
        if "contact your system administrator" in edit_template_content:
            enhancements_found.append("✅ Administrator contact guidance")
        else:
            enhancements_found.append("❌ Missing administrator contact guidance")
        
        print("Edit Profile Template Enhancements:")
        for enhancement in enhancements_found:
            print(f"  {enhancement}")
        
    except FileNotFoundError:
        print("❌ Edit profile template not found")
        return False
    
    # Test 3: Check profile view template
    try:
        with open("templates/institution/institutionprofile.html", "r", encoding="utf-8") as f:
            view_template_content = f.read()
        
        view_enhancements_found = []
        
        if "Official Institution Name" in view_template_content:
            view_enhancements_found.append("✅ Official Institution Name label in view")
        else:
            view_enhancements_found.append("❌ Missing Official Institution Name label in view")
        
        if "Official Institution Email" in view_template_content:
            view_enhancements_found.append("✅ Official Institution Email label in view")
        else:
            view_enhancements_found.append("❌ Missing Official Institution Email label in view")
        
        if "official institution name as registered during account creation" in view_template_content:
            view_enhancements_found.append("✅ Clear explanation in profile view")
        else:
            view_enhancements_found.append("❌ Missing explanation in profile view")
        
        if "Official" in view_template_content and "fas fa-lock" in view_template_content:
            view_enhancements_found.append("✅ Official badges with lock icons")
        else:
            view_enhancements_found.append("❌ Missing official badges")
        
        print("\nProfile View Template Enhancements:")
        for enhancement in view_enhancements_found:
            print(f"  {enhancement}")
        
    except FileNotFoundError:
        print("❌ Profile view template not found")
        return False
    
    # Test 4: Check CSS enhancements
    css_enhancements = []
    
    if ".readonly-hint" in edit_template_content:
        css_enhancements.append("✅ Enhanced readonly hint styles")
    else:
        css_enhancements.append("❌ Missing readonly hint styles")
    
    if ".info-banner" in edit_template_content:
        css_enhancements.append("✅ Information banner styles")
    else:
        css_enhancements.append("❌ Missing information banner styles")
    
    if "background-color: #f1f5f9" in edit_template_content:
        css_enhancements.append("✅ Enhanced hint background styling")
    else:
        css_enhancements.append("❌ Missing enhanced hint styling")
    
    print("\nCSS Enhancements:")
    for enhancement in css_enhancements:
        print(f"  {enhancement}")
    
    # Test 5: Count successful enhancements
    all_enhancements = enhancements_found + view_enhancements_found + css_enhancements
    successful_enhancements = [e for e in all_enhancements if e.startswith("✅")]
    total_enhancements = len(all_enhancements)
    
    print(f"\n📊 Enhancement Summary:")
    print(f"   Total enhancements: {total_enhancements}")
    print(f"   Successful: {len(successful_enhancements)}")
    print(f"   Success rate: {len(successful_enhancements)/total_enhancements*100:.1f}%")
    
    if len(successful_enhancements) == total_enhancements:
        print("\n🎉 All UI enhancements successfully implemented!")
        print("✅ Institution name and email are clearly marked as official and read-only")
        print("✅ Users will understand these fields cannot be edited")
        print("✅ Clear guidance provided for requesting changes")
        return True
    else:
        print(f"\n⚠️  {total_enhancements - len(successful_enhancements)} enhancements missing or incomplete")
        return False

if __name__ == "__main__":
    success = test_ui_enhancements()
    sys.exit(0 if success else 1)