#!/usr/bin/env python3
"""
Script to check if parent consent columns exist in production database
Run this on production server to verify database schema
"""

from app import app, db, MenteeProfile
import sys

def check_parent_consent_columns():
    """Check if parent consent columns exist in database"""
    with app.app_context():
        try:
            # Try to query a mentee profile
            profile = MenteeProfile.query.first()
            
            if not profile:
                print("⚠️  No mentee profiles found in database")
                print("   Creating a test query to check columns...")
                
            # Check if columns exist by trying to access them
            columns_to_check = [
                'parent_email',
                'parent_consent_status', 
                'parent_consent_token',
                'parent_consent_date'
            ]
            
            print("\n" + "="*60)
            print("CHECKING PARENT CONSENT COLUMNS")
            print("="*60 + "\n")
            
            all_exist = True
            for column in columns_to_check:
                try:
                    # Try to access the column
                    if profile:
                        value = getattr(profile, column, None)
                        print(f"✅ {column:30} EXISTS (value: {value})")
                    else:
                        # Check if column exists in model
                        if hasattr(MenteeProfile, column):
                            print(f"✅ {column:30} EXISTS (in model)")
                        else:
                            print(f"❌ {column:30} MISSING")
                            all_exist = False
                except AttributeError:
                    print(f"❌ {column:30} MISSING")
                    all_exist = False
            
            print("\n" + "="*60)
            if all_exist:
                print("✅ SUCCESS: All parent consent columns exist!")
                print("="*60 + "\n")
                return True
            else:
                print("❌ ERROR: Some parent consent columns are missing!")
                print("="*60 + "\n")
                print("SOLUTION:")
                print("Run this command to fix:")
                print("  flask db upgrade")
                print("\nOr manually run:")
                print("  sqlite3 instance/mentors_connect.db < fix_db.sql")
                print("\n")
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
            print("This error means parent consent columns are missing!")
            print("\nSOLUTION:")
            print("1. Run: flask db upgrade")
            print("2. Or run: sqlite3 instance/mentors_connect.db < fix_db.sql")
            print("\n")
            return False

if __name__ == "__main__":
    success = check_parent_consent_columns()
    sys.exit(0 if success else 1)
