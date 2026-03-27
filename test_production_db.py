#!/usr/bin/env python3
"""
Test database connection and parent consent columns
"""
from app import app, db, MenteeProfile, User

print("="*60)
print("TESTING DATABASE CONNECTION")
print("="*60)

with app.app_context():
    try:
        # Test basic query
        user_count = User.query.count()
        print(f"\n✅ Users in database: {user_count}")
        
        # Test mentee profile query
        mentee_count = MenteeProfile.query.count()
        print(f"✅ Mentee profiles: {mentee_count}")
        
        # Test parent consent columns
        profile = MenteeProfile.query.first()
        if profile:
            print(f"\n✅ Testing parent consent columns:")
            print(f"   - parent_email exists: {hasattr(profile, 'parent_email')}")
            print(f"   - parent_consent_status exists: {hasattr(profile, 'parent_consent_status')}")
            print(f"   - parent_consent_token exists: {hasattr(profile, 'parent_consent_token')}")
            print(f"   - parent_consent_date exists: {hasattr(profile, 'parent_consent_date')}")
            
            # Try to access values
            try:
                print(f"\n✅ Sample values:")
                print(f"   - parent_email: {profile.parent_email}")
                print(f"   - parent_consent_status: {profile.parent_consent_status}")
            except Exception as e:
                print(f"\n❌ Error accessing columns: {e}")
                raise
        
        print("\n" + "="*60)
        print("✅ DATABASE CONNECTION SUCCESSFUL!")
        print("="*60)
        
    except Exception as e:
        print(f"\n" + "="*60)
        print(f"❌ ERROR: {e}")
        print("="*60)
        print("\nFull error traceback:")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*60)
        print("SOLUTION:")
        print("="*60)
        print("Run one of these commands:")
        print("  1. flask db upgrade")
        print("  2. sqlite3 instance/mentors_connect.db < fix_db.sql")
        print("="*60)
