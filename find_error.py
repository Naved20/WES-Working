#!/usr/bin/env python3
"""
Find exact error in production
Run this to see what's causing 500 errors
"""

print("="*60)
print("FINDING PRODUCTION ERROR")
print("="*60)

# Test 1: Import app
print("\n1. Testing app import...")
try:
    from app import app
    print("   ✅ App imported successfully")
except Exception as e:
    print(f"   ❌ App import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 2: Test database
print("\n2. Testing database connection...")
try:
    from app import db, User, MenteeProfile
    with app.app_context():
        user_count = User.query.count()
        print(f"   ✅ Database working - {user_count} users")
except Exception as e:
    print(f"   ❌ Database error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test signup route
print("\n3. Testing signup route...")
try:
    with app.test_client() as client:
        response = client.get('/signup')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Signup page loads")
        else:
            print(f"   ❌ Signup page error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Signup route error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test signup POST
print("\n4. Testing signup POST...")
try:
    with app.test_client() as client:
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'Test@123',
            'user_type': '2'
        }
        response = client.post('/signup', data=test_data, follow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 302]:
            print("   ✅ Signup POST works")
        else:
            print(f"   ❌ Signup POST error: {response.status_code}")
            print(f"   Response: {response.data[:500]}")
except Exception as e:
    print(f"   ❌ Signup POST error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check SMTP settings
print("\n5. Checking SMTP configuration...")
try:
    from app import SMTP_EMAIL, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT
    print(f"   SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"   SMTP Email: {SMTP_EMAIL}")
    print(f"   SMTP Password set: {'Yes' if SMTP_PASSWORD else 'No'}")
    
    # Test SMTP connection
    import smtplib
    print("\n   Testing SMTP connection...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.quit()
    print("   ✅ SMTP connection successful")
except Exception as e:
    print(f"   ❌ SMTP error: {e}")
    print("   This might be causing signup failures!")

# Test 6: Check parent consent email function
print("\n6. Testing parent consent email function...")
try:
    from app import send_parent_consent_email
    print("   ✅ Function exists")
except Exception as e:
    print(f"   ❌ Function import error: {e}")

# Test 7: Test request_mentorship route
print("\n7. Testing request_mentorship route...")
try:
    with app.test_client() as client:
        # First login
        client.post('/signin', data={'email': 'test@example.com', 'password': 'test'})
        
        # Try request mentorship
        test_data = {
            'mentor_id': 1,
            'purpose': 'test',
            'mentor_type': 'test',
            'term': 'test',
            'duration_months': 1,
            'why_need_mentor': 'test'
        }
        response = client.post('/request_mentorship', 
                              json=test_data,
                              content_type='application/json')
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 403]:
            print("   ✅ Route accessible")
        else:
            print(f"   ❌ Route error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Request mentorship error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("ERROR CHECK COMPLETE")
print("="*60)
print("\nIf you see errors above, those are causing 500 errors!")
print("Send the output to fix the issues.")
