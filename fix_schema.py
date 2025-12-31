#!/usr/bin/env python
"""
Script to fix the database schema by adding missing columns
"""
import sqlite3

DB_PATH = "instance/mentors_connect.db"

def fix_schema():
    """Add missing columns to signup_details table"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if institution column exists
        cursor.execute("PRAGMA table_info(signup_details)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Current columns in signup_details: {columns}")
        
        if "institution" not in columns:
            print("\n➕ Adding 'institution' column...")
            cursor.execute("ALTER TABLE signup_details ADD COLUMN institution VARCHAR(150)")
            print("✅ Added 'institution' column")
        else:
            print("✅ 'institution' column already exists")
        
        if "institution_id" not in columns:
            print("\n➕ Adding 'institution_id' column...")
            cursor.execute("ALTER TABLE signup_details ADD COLUMN institution_id INTEGER")
            print("✅ Added 'institution_id' column")
        else:
            print("✅ 'institution_id' column already exists")
        
        conn.commit()
        print("\n✅ Schema fix completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
