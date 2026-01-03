#!/usr/bin/env python
"""
Script to delete users with @example.com email and specific email address
"""
import sqlite3

DB_PATH = "instance/mentors_connect.db"

def delete_users():
    """Delete all users with @example.com and mdnavedmansoori20@gmail.com"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get all users to delete
        cursor.execute("""
            SELECT id, email FROM signup_details 
            WHERE email LIKE '%@example.com' OR email = 'mdnavedmansoori20@gmail.com'
        """)
        users_to_delete = cursor.fetchall()
        
        if not users_to_delete:
            print("✅ No users found to delete.")
            return
        
        print(f"Found {len(users_to_delete)} user(s) to delete:")
        for user_id, email in users_to_delete:
            print(f"  - ID: {user_id}, Email: {email}")
        
        user_ids = [user[0] for user in users_to_delete]
        
        # Delete related records first (due to foreign key constraints)
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
        print(f"\n✅ Successfully deleted {len(users_to_delete)} user(s) and all related data.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    delete_users()
