#!/usr/bin/env python
"""
Script to remove all users with @example.com email addresses from the database
"""
import sqlite3
from pathlib import Path

DB_PATH = "instance/mentors_connect.db"

def remove_example_com_users():
    """Remove all users with @example.com email addresses"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # First, get all users with @example.com emails
        cursor.execute("SELECT id, email FROM signup_details WHERE email LIKE '%@example.com'")
        example_users = cursor.fetchall()
        
        if not example_users:
            print("✅ No users with @example.com email found.")
            return
        
        print(f"Found {len(example_users)} user(s) with @example.com email:")
        for user_id, email in example_users:
            print(f"  - ID: {user_id}, Email: {email}")
        
        user_ids = [user[0] for user in example_users]
        
        # Delete related records first (due to foreign key constraints)
        # Order matters - delete from tables that reference signup_details
        
        tables_to_clean = [
            ("mentor_profile", "user_id"),
            ("mentee_profile", "user_id"),
            ("supervisor_profile", "user_id"),
            ("mentorship_requests", "mentee_id"),
            ("mentorship_requests", "mentor_id"),
            ("meeting_requests", "requester_id"),
            ("meeting_requests", "requested_to_id"),
            ("mentee_tasks", "mentee_id"),
            ("mentee_tasks", "mentor_id"),
            ("personal_tasks", "mentee_id"),
            ("personal_tasks", "mentor_id"),
            ("task_ratings", "mentee_id"),
            ("task_ratings", "mentor_id"),
        ]
        
        print("\n🗑️  Deleting related records...")
        for table, column in tables_to_clean:
            for user_id in user_ids:
                cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", (user_id,))
                if cursor.rowcount > 0:
                    print(f"  - Deleted {cursor.rowcount} record(s) from {table} (user_id={user_id})")
        
        # Finally, delete the users from signup_details
        print("\n👤 Deleting users from signup_details...")
        for user_id in user_ids:
            cursor.execute("DELETE FROM signup_details WHERE id = ?", (user_id,))
            print(f"  - Deleted user ID: {user_id}")
        
        conn.commit()
        print(f"\n✅ Successfully removed {len(example_users)} user(s) with @example.com email and all related data.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    remove_example_com_users()
