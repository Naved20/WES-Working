#!/usr/bin/env python3
"""
Quick production error checker
Run this on production server to diagnose issues
"""
import sys
import os

print("="*60)
print("PRODUCTION ERROR CHECKER")
print("="*60)

# Check 1: Python version
print(f"\n1. Python version: {sys.version}")

# Check 2: Check if app.py exists
print(f"2. app.py exists: {os.path.exists('app.py')}")

# Check 3: Check if database exists
print(f"3. Database exists: {os.path.exists('instance/mentors_connect.db')}")

# Check 4: Check database permissions
if os.path.exists('instance/mentors_connect.db'):
    import stat
    st = os.stat('instance/mentors_connect.db')
    print(f"4. Database permissions: {oct(st.st_mode)[-3:]}")

# Check 5: Try importing app
try:
    from app import app
    print("5. ✅ App import successful")
except Exception as e:
    print(f"5. ❌ App import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check 6: Try importing database
try:
    from app import db, MenteeProfile
    print("6. ✅ Database models import successful")
except Exception as e:
    print(f"6. ❌ Database import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check 7: Test database connection
try:
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"7. ✅ Database tables: {len(tables)} tables found")
        
        # Check if mentee_profile table exists
        if 'mentee_profile' in tables:
            columns = [col['name'] for col in inspector.get_columns('mentee_profile')]
            print(f"8. ✅ mentee_profile columns: {len(columns)} columns")
            
            # Check parent consent columns
            required_cols = ['parent_email', 'parent_consent_status', 'parent_consent_token', 'parent_consent_date']
            missing = [col for col in required_cols if col not in columns]
            
            if missing:
                print(f"9. ❌ MISSING COLUMNS: {missing}")
                print("\n   FIX: Run 'flask db upgrade' or 'sqlite3 instance/mentors_connect.db < fix_db.sql'")
            else:
                print(f"9. ✅ All parent consent columns exist")
                
            # Show all columns
            print(f"\n   All columns in mentee_profile:")
            for col in columns:
                print(f"      - {col}")
        else:
            print("8. ❌ mentee_profile table not found!")
            
except Exception as e:
    print(f"7. ❌ Database connection failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Check complete!")
print("="*60)
